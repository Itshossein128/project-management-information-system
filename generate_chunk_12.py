import json
import re
import os

def normalize_id(text):
    # lowercase, replace non-alphanumeric chars with _
    res = re.sub(r'[^a-z0-9]+', '_', text.lower()).strip('_')
    return res if res else "entity"

def make_node_id(source_file, entity):
    repo_root = "/home/hossein/Desktop/projects/mehdi/building-management"
    rel_path = os.path.relpath(source_file, repo_root)
    stem, _ = os.path.splitext(rel_path)
    stem_norm = normalize_id(stem)
    entity_norm = normalize_id(entity)
    return f"{stem_norm}_{entity_norm}"

nodes = []
edges = []
hyperedges = []

def add_node(source_file, entity, label, file_type="document", rationale=None):
    nid = make_node_id(source_file, entity)
    node = {
        "id": nid,
        "label": label,
        "file_type": file_type,
        "source_file": source_file,
        "source_location": None,
        "source_url": None,
        "captured_at": None,
        "author": None,
        "contributor": None
    }
    if rationale:
        node["rationale"] = rationale
    nodes.append(node)
    return nid

def add_edge(source_file, source_id, target_id, relation, confidence="EXTRACTED", confidence_score=1.0, weight=1.0):
    edges.append({
        "source": source_id,
        "target": target_id,
        "relation": relation,
        "confidence": confidence,
        "confidence_score": confidence_score,
        "source_file": source_file,
        "source_location": None,
        "weight": weight
    })

def add_hyperedge(source_file, hid, label, node_ids, relation="form", confidence="INFERRED", confidence_score=0.85):
    hyperedges.append({
        "id": hid,
        "label": label,
        "nodes": node_ids,
        "relation": relation,
        "confidence": confidence,
        "confidence_score": confidence_score,
        "source_file": source_file
    })

# 1. apps/web/playwright-report/index.html
f1 = "/home/hossein/Desktop/projects/mehdi/building-management/apps/web/playwright-report/index.html"
n_playwright = add_node(f1, "PlaywrightTestReport", "Playwright Test Report", "document")
n_zipjs = add_node(f1, "ZipJsInflateEngine", "Zip.js Inflate Engine", "code")
add_edge(f1, n_playwright, n_zipjs, "references", "EXTRACTED", 1.0)

# 2. apps/web/public/robots.txt
f2 = "/home/hossein/Desktop/projects/mehdi/building-management/apps/web/public/robots.txt"
n_robots = add_node(f2, "RobotsCrawlPolicy", "Robots.txt Crawl Policy", "document")

# 3. apps/web/src/app/ROUTES.md
f3 = "/home/hossein/Desktop/projects/mehdi/building-management/apps/web/src/app/ROUTES.md"
n_web_routing = add_node(f3, "FrontendRoutingArchitecture", "Frontend Routing Architecture", "document")
n_routevars = add_node(f3, "RouteVarsRegistry", "routeVars.ts Registry", "code")
n_routests = add_node(f3, "RootRoutesConfig", "routes.ts Root Config", "code")
n_auth_routes = add_node(f3, "AuthRoutesModule", "auth.routes.ts Module", "code")
n_hr_routes = add_node(f3, "HrRoutesModule", "hr.routes.ts Module", "code")
n_biz_setup_routes = add_node(f3, "BusinessSetupRoutesModule", "business-setup.routes.ts Module", "code")
n_biz_routes = add_node(f3, "BusinessRoutesModule", "business.routes.ts Module", "code")

add_edge(f3, n_web_routing, n_routevars, "references", "EXTRACTED", 1.0)
add_edge(f3, n_web_routing, n_routests, "references", "EXTRACTED", 1.0)
add_edge(f3, n_routests, n_biz_setup_routes, "references", "EXTRACTED", 1.0)
add_edge(f3, n_routests, n_auth_routes, "conceptually_related_to", "INFERRED", 0.85)
add_edge(f3, n_routests, n_hr_routes, "conceptually_related_to", "INFERRED", 0.85)
add_edge(f3, n_routests, n_biz_routes, "conceptually_related_to", "INFERRED", 0.85)

# 4. apps/web/src/app/routes/ROUTES.md
f4 = "/home/hossein/Desktop/projects/mehdi/building-management/apps/web/src/app/routes/ROUTES.md"
n_modular_routes = add_node(f4, "ModularRouteConfigurations", "Modular Route Configurations", "document")
n_proj_route_chunk = add_node(f4, "ProjectWorkspaceRouteChunk", "Project Workspace Route Chunk", "concept")
add_edge(f4, n_modular_routes, n_proj_route_chunk, "references", "EXTRACTED", 1.0)
add_edge(f4, n_proj_route_chunk, n_biz_setup_routes, "references", "EXTRACTED", 1.0)

# 5. customer/README.md
f5 = "/home/hossein/Desktop/projects/mehdi/building-management/customer/README.md"
n_cust_deploy = add_node(f5, "VeronaStandaloneDeployment", "Verona Standalone Customer Deployment", "document")
n_cust_launchers = add_node(f5, "CustomerLauncherScripts", "Customer Launcher Scripts (.bat / .sh)", "code")
n_cust_prebuild = add_node(f5, "CustomerPrebuildPipeline", "Customer Pre-build Image Pipeline", "concept")
n_cust_config = add_node(f5, "CustomerEnvironmentConfig", "customer/ipcas.config Configuration", "code")

add_edge(f5, n_cust_deploy, n_cust_launchers, "references", "EXTRACTED", 1.0)
add_edge(f5, n_cust_deploy, n_cust_prebuild, "references", "EXTRACTED", 1.0)
add_edge(f5, n_cust_deploy, n_cust_config, "references", "EXTRACTED", 1.0)

# 6. docker-compose.customer.yml
f6 = "/home/hossein/Desktop/projects/mehdi/building-management/docker-compose.customer.yml"
n_dc_cust_pg = add_node(f6, "PostgresCustomerService", "PostgreSQL Service (Customer Stack)", "code")
n_dc_cust_rmq = add_node(f6, "RabbitmqCustomerService", "RabbitMQ Service (Customer Stack)", "code")
n_dc_cust_minio = add_node(f6, "MinioCustomerService", "MinIO Storage Service (Customer Stack)", "code")
n_dc_cust_redis = add_node(f6, "RedisCustomerService", "Redis Cache Service (Customer Stack)", "code")
n_dc_cust_api = add_node(f6, "ApiCustomerService", "Django API Service (Customer Stack)", "code")
n_dc_cust_web = add_node(f6, "WebCustomerService", "React Web Service (Customer Stack)", "code")
n_dc_cust_traefik = add_node(f6, "TraefikCustomerService", "Traefik Gateway Service (Customer Stack)", "code")
n_dc_cust_worker = add_node(f6, "EventWorkerCustomerService", "Event Worker Service (Customer Stack)", "code")

add_edge(f6, n_dc_cust_api, n_dc_cust_pg, "references", "EXTRACTED", 1.0)
add_edge(f6, n_dc_cust_api, n_dc_cust_rmq, "references", "EXTRACTED", 1.0)
add_edge(f6, n_dc_cust_api, n_dc_cust_minio, "references", "EXTRACTED", 1.0)
add_edge(f6, n_dc_cust_api, n_dc_cust_redis, "references", "EXTRACTED", 1.0)
add_edge(f6, n_dc_cust_worker, n_dc_cust_rmq, "references", "EXTRACTED", 1.0)
add_edge(f6, n_dc_cust_traefik, n_dc_cust_web, "references", "EXTRACTED", 1.0)
add_edge(f6, n_dc_cust_traefik, n_dc_cust_api, "references", "EXTRACTED", 1.0)
add_edge(f6, n_dc_cust_api, n_cust_deploy, "semantically_similar_to", "INFERRED", 0.95)

# 7. docker-compose.yml
f7 = "/home/hossein/Desktop/projects/mehdi/building-management/docker-compose.yml"
n_dc_pg = add_node(f7, "PostgresDevService", "PostgreSQL Service (Dev Stack)", "code")
n_dc_rmq = add_node(f7, "RabbitmqDevService", "RabbitMQ Service (Dev Stack)", "code")
n_dc_minio = add_node(f7, "MinioDevService", "MinIO Storage Service (Dev Stack)", "code")
n_dc_redis = add_node(f7, "RedisDevService", "Redis Cache Service (Dev Stack)", "code")
n_dc_api = add_node(f7, "ApiDevService", "Django API Service (Dev Stack)", "code")
n_dc_web = add_node(f7, "WebDevService", "React Web Service (Dev Stack)", "code")
n_dc_traefik = add_node(f7, "TraefikDevService", "Traefik Gateway Service (Dev Stack)", "code")

add_edge(f7, n_dc_api, n_dc_pg, "references", "EXTRACTED", 1.0)
add_edge(f7, n_dc_api, n_dc_rmq, "references", "EXTRACTED", 1.0)
add_edge(f7, n_dc_api, n_dc_minio, "references", "EXTRACTED", 1.0)
add_edge(f7, n_dc_api, n_dc_redis, "references", "EXTRACTED", 1.0)
add_edge(f7, n_dc_traefik, n_dc_web, "references", "EXTRACTED", 1.0)
add_edge(f7, n_dc_traefik, n_dc_api, "references", "EXTRACTED", 1.0)

# Semantically similar edges between customer stack and dev stack
add_edge(f7, n_dc_cust_api, n_dc_api, "semantically_similar_to", "INFERRED", 0.95)
add_edge(f7, n_dc_cust_traefik, n_dc_traefik, "semantically_similar_to", "INFERRED", 0.95)

# 8. e2e/COVERAGE_MAP.md
f8 = "/home/hossein/Desktop/projects/mehdi/building-management/e2e/COVERAGE_MAP.md"
n_e2e_cov = add_node(f8, "VeronaE2ECoverageMap", "Verona E2E Coverage Map", "document")
n_auth_prio = add_node(f8, "AuthPriorityQueue", "Auth E2E Test Priority Queue", "concept")
add_edge(f8, n_e2e_cov, n_auth_prio, "references", "EXTRACTED", 1.0)

# 9. e2e/DAILY_LOG.md
f9 = "/home/hossein/Desktop/projects/mehdi/building-management/e2e/DAILY_LOG.md"
n_e2e_log = add_node(f9, "VeronaE2EDailyLog", "Verona E2E Daily Test Log", "document")
add_edge(f9, n_e2e_log, n_e2e_cov, "conceptually_related_to", "INFERRED", 0.85)

# 10. e2e/DATA_TESTIDS.md
f10 = "/home/hossein/Desktop/projects/mehdi/building-management/e2e/DATA_TESTIDS.md"
n_testids = add_node(f10, "DataTestIdsMasterList", "Data TestIDs Master List", "document")
add_edge(f10, n_testids, n_e2e_cov, "conceptually_related_to", "INFERRED", 0.85)
add_edge(f10, n_testids, n_auth_routes, "references", "EXTRACTED", 1.0)

# 11. graphify-out/converted/درخواست خرید ها_e0566ada.md
f11 = "/home/hossein/Desktop/projects/mehdi/building-management/graphify-out/converted/درخواست خرید ها_e0566ada.md"
n_prd_mr = add_node(f11, "SmartProcurementPRD", "Smart Logistics & Procurement PRD", "document", 
                    rationale="Eliminate physical paper workflows, isolate block inventory, and enforce strict sequential MR approval hierarchy.")
n_block_trace = add_node(f11, "BlockBasedTraceability", "Block-Based Material Traceability", "concept",
                    rationale="Prevent construction materials designated for Block A from being utilized in Block B.")
n_mr_workflow = add_node(f11, "MaterialRequisitionWorkflow", "Material Requisition Sequential Workflow", "rationale",
                    rationale="Strict state machine without step overrides, forcing linear approvals from job site execution to executive finance.")
n_inventory_lock = add_node(f11, "BlockLevelInventoryLock", "Block-Level Inventory Lock & Tagging", "concept",
                    rationale="Tag GRN stock with [MR-ID] + [Block-ID] to create reserved stock accessible only by authorized block users.")

add_edge(f11, n_prd_mr, n_block_trace, "references", "EXTRACTED", 1.0)
add_edge(f11, n_prd_mr, n_mr_workflow, "references", "EXTRACTED", 1.0)
add_edge(f11, n_prd_mr, n_inventory_lock, "references", "EXTRACTED", 1.0)
add_edge(f11, n_inventory_lock, n_block_trace, "rationale_for", "EXTRACTED", 1.0)

# 12. graphify-out/converted/طرح اولیه سیستم اتوماسیون یکپارچه کنترل پروژه_rev2_c441e8a6.md
f12 = "/home/hossein/Desktop/projects/mehdi/building-management/graphify-out/converted/طرح اولیه سیستم اتوماسیون یکپارچه کنترل پروژه_rev2_c441e8a6.md"
n_blueprint = add_node(f12, "ProjectControlAutomationBlueprint", "Project Control Automation System Blueprint", "document",
                       rationale="Centralize construction project data connecting physical execution, cash flow, time schedules, and contractual IPCs.")
n_wbs_engine = add_node(f12, "WbsControlEngine", "WBS Control Engine", "concept",
                       rationale="Serve as the backbone linking time schedule, progress, cost, contractor IPCs, and daily reports.")
n_progress_control = add_node(f12, "PhysicalFinancialProgressControl", "Physical & Financial Progress Control", "concept",
                       rationale="Track planned vs actual physical progress and variance metrics to forecast completion dates.")

add_edge(f12, n_blueprint, n_wbs_engine, "references", "EXTRACTED", 1.0)
add_edge(f12, n_blueprint, n_progress_control, "references", "EXTRACTED", 1.0)
add_edge(f12, n_wbs_engine, n_progress_control, "conceptually_related_to", "INFERRED", 0.95)
add_edge(f12, n_prd_mr, n_blueprint, "semantically_similar_to", "INFERRED", 0.85)

# Hyperedges
add_hyperedge(f3, "frontend_routing_stack", "Frontend Modular Routing Stack", [n_web_routing, n_routests, n_biz_setup_routes, n_auth_routes], "participate_in", "INFERRED", 0.85)
add_hyperedge(f6, "customer_docker_stack", "Verona Standalone Customer Stack Services", [n_dc_cust_api, n_dc_cust_web, n_dc_cust_traefik, n_dc_cust_pg, n_dc_cust_redis], "participate_in", "INFERRED", 0.95)
add_hyperedge(f8, "e2e_testing_suite", "Verona E2E Testing & Quality Framework", [n_e2e_cov, n_e2e_log, n_testids, n_playwright], "participate_in", "INFERRED", 0.85)

output = {
    "nodes": nodes,
    "edges": edges,
    "hyperedges": hyperedges,
    "input_tokens": 0,
    "output_tokens": 0
}

out_path = "/home/hossein/Desktop/projects/mehdi/building-management/graphify-out/.graphify_chunk_12.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("Generated graphify chunk 12 successfully with", len(nodes), "nodes,", len(edges), "edges,", len(hyperedges), "hyperedges.")
