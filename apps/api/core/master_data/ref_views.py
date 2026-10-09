"""Org-wide reference APIs: OrganizationUnit, ManagedContractType."""
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from master_data.models import ManagedContractType, OrganizationUnit
from master_data.ref_serializers import ManagedContractTypeSerializer, OrganizationUnitSerializer


class OrganizationUnitListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary='List organization units', tags=['Central Data'])
    def get(self, request):
        qs = OrganizationUnit.objects.all()
        return Response(OrganizationUnitSerializer(qs, many=True).data)

    @extend_schema(summary='Create organization unit', tags=['Central Data'])
    def post(self, request):
        serializer = OrganizationUnitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        parent = serializer.validated_data.get('parent')
        if parent and parent.parent_id == parent.id:
            return Response({'code': 'invalid_parent'}, status=400)
        obj = OrganizationUnit.objects.create(
            **serializer.validated_data,
            created_by=request.user,
            updated_by=request.user,
        )
        return Response(OrganizationUnitSerializer(obj).data, status=status.HTTP_201_CREATED)


class OrganizationUnitDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary='Update organization unit', tags=['Central Data'])
    def patch(self, request, pk):
        obj = get_object_or_404(OrganizationUnit, pk=pk)
        serializer = OrganizationUnitSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        for k, v in serializer.validated_data.items():
            setattr(obj, k, v)
        obj.updated_by = request.user
        obj.save()
        return Response(OrganizationUnitSerializer(obj).data)


class ManagedContractTypeListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary='List managed contract types', tags=['Central Data'])
    def get(self, request):
        qs = ManagedContractType.objects.filter(is_active=True)
        if request.query_params.get('all') == '1':
            qs = ManagedContractType.objects.all()
        return Response(ManagedContractTypeSerializer(qs, many=True).data)

    @extend_schema(summary='Create managed contract type', tags=['Central Data'])
    def post(self, request):
        serializer = ManagedContractTypeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = ManagedContractType.objects.create(**serializer.validated_data)
        return Response(ManagedContractTypeSerializer(obj).data, status=status.HTTP_201_CREATED)
