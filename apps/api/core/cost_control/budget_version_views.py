"""Budget versions, change requests, remaining, and transfers."""

from decimal import Decimal, InvalidOperation

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cost_control.models import Budget, BudgetChangeRequest, BudgetVersion
from cost_control.serializers import (
    BudgetChangeRequestCreateSerializer,
    BudgetChangeRequestSerializer,
    BudgetSerializer,
    BudgetTransferCreateSerializer,
    BudgetTransferSerializer,
    BudgetVersionCreateSerializer,
    BudgetVersionSerializer,
)
from cost_control.services import budget_change_service as change_svc
from cost_control.services import budget_version_service as version_svc
from cost_control.services.budget_service import assert_line_mutable, budget_summary
from cost_control.services.remaining_service import remaining_allocatable, transfer_budget
from permissions.project import HasProjectPermission, IsProjectMember


class BudgetVersionListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]

    @property
    def required_permission(self):
        return 'view_costs' if self.request.method == 'GET' else 'edit_costs'

    @extend_schema(summary='List budget versions', tags=['Cost control'])
    def get(self, request, project_pk=None):
        qs = BudgetVersion.objects.filter(project_id=project_pk, is_deleted=False)
        return Response(BudgetVersionSerializer(qs, many=True).data)

    @extend_schema(summary='Create budget version draft', tags=['Cost control'])
    def post(self, request, project_pk=None):
        ser = BudgetVersionCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        version = version_svc.create_version(
            project_id=project_pk,
            user=request.user,
            **ser.validated_data,
        )
        return Response(BudgetVersionSerializer(version).data, status=status.HTTP_201_CREATED)


class BudgetVersionDetailView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]

    @property
    def required_permission(self):
        return 'view_costs' if self.request.method == 'GET' else 'edit_costs'

    def get_object(self, project_pk, pk):
        return get_object_or_404(BudgetVersion, pk=pk, project_id=project_pk, is_deleted=False)

    @extend_schema(summary='Retrieve budget version', tags=['Cost control'])
    def get(self, request, project_pk=None, pk=None):
        return Response(BudgetVersionSerializer(self.get_object(project_pk, pk)).data)

    @extend_schema(summary='Patch draft budget version', tags=['Cost control'])
    def patch(self, request, project_pk=None, pk=None):
        version = self.get_object(project_pk, pk)
        version_svc.assert_version_editable(version)
        for field in ('name', 'notes', 'currency'):
            if field in request.data:
                setattr(version, field, request.data.get(field) or '')
        version.updated_by = request.user
        version.save()
        return Response(BudgetVersionSerializer(version).data)


class BudgetVersionActionView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]

    def get_required_permission(self):
        action_name = self.kwargs.get('action_name')
        if action_name in ('approve', 'reject'):
            return 'approve_costs'
        return 'edit_costs'

    @property
    def required_permission(self):
        return self.get_required_permission()

    @extend_schema(summary='Budget version lifecycle action', tags=['Cost control'])
    def post(self, request, project_pk=None, pk=None, action_name=None):
        version = get_object_or_404(
            BudgetVersion, pk=pk, project_id=project_pk, is_deleted=False
        )
        if action_name == 'submit':
            version = version_svc.submit_version(version, request.user)
        elif action_name == 'approve':
            promote = bool(request.data.get('promote_to_control'))
            version = version_svc.approve_version(
                version, request.user, promote_to_control=promote
            )
        elif action_name == 'reject':
            version = version_svc.reject_version(
                version, request.user, reason=request.data.get('reason', '')
            )
        else:
            return Response({'detail': 'Unknown action'}, status=status.HTTP_404_NOT_FOUND)
        return Response(BudgetVersionSerializer(version).data)


class BudgetVersionCompareView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_costs'

    @extend_schema(summary='Compare two budget versions', tags=['Cost control'])
    def get(self, request, project_pk=None):
        left_id = request.query_params.get('left')
        right_id = request.query_params.get('right')
        if not left_id or not right_id:
            return Response(
                {'detail': 'left and right query params are required'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        left = get_object_or_404(
            BudgetVersion, pk=left_id, project_id=project_pk, is_deleted=False
        )
        right = get_object_or_404(
            BudgetVersion, pk=right_id, project_id=project_pk, is_deleted=False
        )
        fx = request.query_params.get('fx_rate')
        fx_rate = None
        if fx not in (None, ''):
            try:
                fx_rate = Decimal(str(fx))
            except (InvalidOperation, TypeError):
                return Response(
                    {'detail': 'Invalid fx_rate'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(version_svc.compare_versions(left, right, fx_rate=fx_rate))


class BudgetVersionLinesView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]

    @property
    def required_permission(self):
        return 'view_costs' if self.request.method == 'GET' else 'edit_costs'

    def get_version(self, project_pk, version_id):
        return get_object_or_404(
            BudgetVersion, pk=version_id, project_id=project_pk, is_deleted=False
        )

    @extend_schema(summary='List lines for a budget version', tags=['Cost control'])
    def get(self, request, project_pk=None, version_id=None):
        version = self.get_version(project_pk, version_id)
        lines = Budget.objects.filter(version=version, is_deleted=False).select_related(
            'wbs', 'activity', 'cbs', 'contract'
        )
        return Response(
            {
                'results': BudgetSerializer(lines, many=True).data,
                'summary': budget_summary(project_pk, version_id=version.id),
            }
        )

    @extend_schema(summary='Create line on draft budget version', tags=['Cost control'])
    def post(self, request, project_pk=None, version_id=None):
        version = self.get_version(project_pk, version_id)
        version_svc.assert_version_editable(version)
        ser = BudgetSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        line = ser.save(
            project_id=project_pk,
            version=version,
            created_by=request.user,
            updated_by=request.user,
        )
        return Response(BudgetSerializer(line).data, status=status.HTTP_201_CREATED)


class BudgetLineDetailView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]

    @property
    def required_permission(self):
        return 'view_costs' if self.request.method == 'GET' else 'edit_costs'

    def get_line(self, project_pk, pk):
        return get_object_or_404(Budget, pk=pk, project_id=project_pk, is_deleted=False)

    def get(self, request, project_pk=None, pk=None):
        return Response(BudgetSerializer(self.get_line(project_pk, pk)).data)

    def patch(self, request, project_pk=None, pk=None):
        line = self.get_line(project_pk, pk)
        assert_line_mutable(line)
        ser = BudgetSerializer(line, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save(updated_by=request.user)
        return Response(ser.data)

    def delete(self, request, project_pk=None, pk=None):
        line = self.get_line(project_pk, pk)
        assert_line_mutable(line)
        line.soft_delete(user=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class BudgetChangeRequestListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]

    @property
    def required_permission(self):
        return 'view_costs' if self.request.method == 'GET' else 'edit_costs'

    @extend_schema(summary='List budget change requests', tags=['Cost control'])
    def get(self, request, project_pk=None):
        qs = change_svc.list_change_requests(project_pk)
        return Response(BudgetChangeRequestSerializer(qs, many=True).data)

    @extend_schema(summary='Create budget change request', tags=['Cost control'])
    def post(self, request, project_pk=None):
        ser = BudgetChangeRequestCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        cr = change_svc.create_change_request(
            project_id=project_pk,
            user=request.user,
            **ser.validated_data,
        )
        return Response(
            BudgetChangeRequestSerializer(cr).data, status=status.HTTP_201_CREATED
        )


class BudgetChangeRequestDetailView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]

    @property
    def required_permission(self):
        return 'view_costs' if self.request.method == 'GET' else 'edit_costs'

    def get_object(self, project_pk, pk):
        return get_object_or_404(
            BudgetChangeRequest, pk=pk, project_id=project_pk, is_deleted=False
        )

    def get(self, request, project_pk=None, pk=None):
        return Response(BudgetChangeRequestSerializer(self.get_object(project_pk, pk)).data)

    def patch(self, request, project_pk=None, pk=None):
        cr = self.get_object(project_pk, pk)
        fields = {}
        for key in ('reason', 'project_impact', 'amount_delta', 'affected_lines'):
            if key in request.data:
                fields[key] = request.data[key]
        cr = change_svc.update_change_request(cr, request.user, **fields)
        return Response(BudgetChangeRequestSerializer(cr).data)


class BudgetChangeRequestActionView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]

    def get_required_permission(self):
        action_name = self.kwargs.get('action_name')
        if action_name in ('approve', 'reject'):
            return 'approve_costs'
        return 'edit_costs'

    @property
    def required_permission(self):
        return self.get_required_permission()

    @extend_schema(summary='Budget change request action', tags=['Cost control'])
    def post(self, request, project_pk=None, pk=None, action_name=None):
        cr = get_object_or_404(
            BudgetChangeRequest, pk=pk, project_id=project_pk, is_deleted=False
        )
        notes = request.data.get('decision_notes', '')
        if action_name == 'submit':
            cr = change_svc.submit_change_request(cr, request.user)
        elif action_name == 'approve':
            cr = change_svc.approve_change_request(cr, request.user, notes)
        elif action_name == 'reject':
            cr = change_svc.reject_change_request(cr, request.user, notes)
        elif action_name == 'cancel':
            cr = change_svc.cancel_change_request(cr, request.user)
        else:
            return Response({'detail': 'Unknown action'}, status=status.HTTP_404_NOT_FOUND)
        return Response(BudgetChangeRequestSerializer(cr).data)


class BudgetRemainingView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_costs'

    @extend_schema(summary='Remaining allocatable by heading', tags=['Cost control'])
    def get(self, request, project_pk=None):
        version_id = request.query_params.get('version_id')
        return Response(remaining_allocatable(project_pk, version_id=version_id))


class BudgetTransferView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'edit_costs'

    @extend_schema(summary='Transfer amount between budget lines', tags=['Cost control'])
    def post(self, request, project_pk=None):
        ser = BudgetTransferCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        transfer = transfer_budget(
            project_id=project_pk,
            user=request.user,
            **ser.validated_data,
        )
        return Response(
            {
                'transfer': BudgetTransferSerializer(transfer).data,
                'from_line': BudgetSerializer(transfer.from_line).data,
                'to_line': BudgetSerializer(transfer.to_line).data,
            },
            status=status.HTTP_201_CREATED,
        )
