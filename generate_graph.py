import json, os, re

repo_root = '/home/hossein/Desktop/projects/mehdi/building-management'

files = [
    '/home/hossein/Desktop/projects/mehdi/building-management/.cursor/skills/brand/SKILL.md',
    '/home/hossein/Desktop/projects/mehdi/building-management/.cursor/skills/brand/references/approval-checklist.md',
    '/home/hossein/Desktop/projects/mehdi/building-management/.cursor/skills/brand/references/asset-organization.md',
    '/home/hossein/Desktop/projects/mehdi/building-management/.cursor/skills/brand/references/brand-guideline-template.md',
    '/home/hossein/Desktop/projects/mehdi/building-management/.cursor/skills/brand/references/color-palette-management.md',
    '/home/hossein/Desktop/projects/mehdi/building-management/.cursor/skills/brand/references/consistency-checklist.md',
    '/home/hossein/Desktop/projects/mehdi/building-management/.cursor/skills/brand/references/logo-usage-rules.md',
    '/home/hossein/Desktop/projects/mehdi/building-management/.cursor/skills/brand/references/messaging-framework.md',
    '/home/hossein/Desktop/projects/mehdi/building-management/.cursor/skills/brand/references/typography-specifications.md',
    '/home/hossein/Desktop/projects/mehdi/building-management/.cursor/skills/brand/references/update.md',
    '/home/hossein/Desktop/projects/mehdi/building-management/.cursor/skills/brand/references/visual-identity.md',
    '/home/hossein/Desktop/projects/mehdi/building-management/.cursor/skills/brand/references/voice-framework.md',
    '/home/hossein/Desktop/projects/mehdi/building-management/.cursor/skills/brand/templates/brand-guidelines-starter.md',
    '/home/hossein/Desktop/projects/mehdi/building-management/.cursor/skills/design-system/SKILL.md',
    '/home/hossein/Desktop/projects/mehdi/building-management/.cursor/skills/design-system/references/component-specs.md',
    '/home/hossein/Desktop/projects/mehdi/building-management/.cursor/skills/design-system/references/component-tokens.md',
    '/home/hossein/Desktop/projects/mehdi/building-management/.cursor/skills/design-system/references/primitive-tokens.md',
    '/home/hossein/Desktop/projects/mehdi/building-management/.cursor/skills/design-system/references/semantic-tokens.md',
    '/home/hossein/Desktop/projects/mehdi/building-management/.cursor/skills/design-system/references/states-and-variants.md',
    '/home/hossein/Desktop/projects/mehdi/building-management/.cursor/skills/design-system/references/tailwind-integration.md',
    '/home/hossein/Desktop/projects/mehdi/building-management/.cursor/skills/design-system/references/token-architecture.md',
    '/home/hossein/Desktop/projects/mehdi/building-management/.cursor/skills/design/SKILL.md'
]

def get_stem(abs_path):
    rel_path = os.path.relpath(abs_path, repo_root)
    path_no_ext, _ = os.path.splitext(rel_path)
    segments = path_no_ext.split(os.sep)
    norm_segments = [re.sub(r'[^a-z0-9]', '_', seg.lower()) for seg in segments]
    return '_'.join(norm_segments)

nodes = []
edges = []
hyperedges = []

def add_node(entity, label, file_type, source_file, author=None):
    stem = get_stem(source_file)
    norm_entity = re.sub(r'[^a-z0-9]', '_', entity.lower())
    node_id = f"{stem}_{norm_entity}"
    nodes.append({
        "id": node_id,
        "label": label,
        "file_type": file_type,
        "source_file": source_file,
        "source_location": None,
        "source_url": None,
        "captured_at": None,
        "author": author,
        "contributor": None
    })
    return node_id

def add_edge(source_id, target_id, relation, confidence, confidence_score, source_file, weight=1.0):
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

def add_hyperedge(hid, label, node_ids, relation, confidence, confidence_score, source_file):
    hyperedges.append({
        "id": hid,
        "label": label,
        "nodes": node_ids,
        "relation": relation,
        "confidence": confidence,
        "confidence_score": confidence_score,
        "source_file": source_file
    })

# 1. brand/SKILL.md
f0 = files[0]
n0_1 = add_node("brand_skill", "Brand Skill System", "concept", f0, author="claudekit")
n0_2 = add_node("brand_voice_guidance", "Brand Voice Guidance", "concept", f0, author="claudekit")
n0_3 = add_node("brand_visual_identity_standards", "Brand Visual Identity Standards", "concept", f0, author="claudekit")
n0_4 = add_node("brand_messaging_framework_definition", "Brand Messaging Framework Definition", "concept", f0, author="claudekit")

add_edge(n0_1, n0_2, "references", "EXTRACTED", 1.0, f0)
add_edge(n0_1, n0_3, "references", "EXTRACTED", 1.0, f0)
add_edge(n0_1, n0_4, "references", "EXTRACTED", 1.0, f0)

# 2. brand/references/approval-checklist.md
f1 = files[1]
n1_1 = add_node("approval_checklist", "Brand Approval Checklist", "concept", f1)
n1_2 = add_node("visual_identity_approval", "Visual Identity Approval", "concept", f1)
n1_3 = add_node("voice_tone_approval", "Voice and Tone Approval", "concept", f1)
n1_4 = add_node("messaging_copy_approval", "Messaging and Copy Approval", "concept", f1)

add_edge(n1_1, n1_2, "references", "EXTRACTED", 1.0, f1)
add_edge(n1_1, n1_3, "references", "EXTRACTED", 1.0, f1)
add_edge(n1_1, n1_4, "references", "EXTRACTED", 1.0, f1)
add_edge(n0_1, n1_1, "references", "EXTRACTED", 1.0, f0)

# 3. brand/references/asset-organization.md
f2 = files[2]
n2_1 = add_node("asset_organization_guide", "Brand Asset Organization Guide", "concept", f2)
n2_2 = add_node("asset_naming_convention", "Asset Naming Convention", "concept", f2)
n2_3 = add_node("asset_metadata_schema", "Asset Metadata Schema", "concept", f2)

add_edge(n2_1, n2_2, "references", "EXTRACTED", 1.0, f2)
add_edge(n2_1, n2_3, "references", "EXTRACTED", 1.0, f2)
add_edge(n0_1, n2_1, "references", "EXTRACTED", 1.0, f0)

# 4. brand/references/brand-guideline-template.md
f3 = files[3]
n3_1 = add_node("brand_guidelines_template", "Brand Guidelines Template", "document", f3)
add_edge(n0_1, n3_1, "references", "EXTRACTED", 1.0, f0)

# 5. brand/references/color-palette-management.md
f4 = files[4]
n4_1 = add_node("color_palette_management", "Color Palette Management", "concept", f4)
n4_2 = add_node("color_system_hierarchy", "Color System Hierarchy", "concept", f4)
n4_3 = add_node("wcag_contrast_requirements", "WCAG Contrast Requirements", "rationale", f4)

add_edge(n4_1, n4_2, "references", "EXTRACTED", 1.0, f4)
add_edge(n4_1, n4_3, "rationale_for", "EXTRACTED", 1.0, f4)
add_edge(n0_1, n4_1, "references", "EXTRACTED", 1.0, f0)

# 6. brand/references/consistency-checklist.md
f5 = files[5]
n5_1 = add_node("consistency_checklist", "Brand Consistency Checklist", "concept", f5)
add_edge(n0_1, n5_1, "references", "EXTRACTED", 1.0, f0)
add_edge(n5_1, n1_1, "semantically_similar_to", "INFERRED", 0.85, f5)

# 7. brand/references/logo-usage-rules.md
f6 = files[6]
n6_1 = add_node("logo_usage_rules", "Logo Usage Rules", "concept", f6)
n6_2 = add_node("logo_clear_space", "Logo Clear Space", "rationale", f6)
n6_3 = add_node("logo_minimum_size", "Logo Minimum Size", "concept", f6)

add_edge(n6_1, n6_2, "references", "EXTRACTED", 1.0, f6)
add_edge(n6_1, n6_3, "references", "EXTRACTED", 1.0, f6)
add_edge(n0_1, n6_1, "references", "EXTRACTED", 1.0, f0)

# 8. brand/references/messaging-framework.md
f7 = files[7]
n7_1 = add_node("messaging_framework", "Messaging Framework", "concept", f7)
n7_2 = add_node("core_brand_statements", "Core Brand Statements", "concept", f7)

add_edge(n7_1, n7_2, "references", "EXTRACTED", 1.0, f7)
add_edge(n0_1, n7_1, "references", "EXTRACTED", 1.0, f0)

# 9. brand/references/typography-specifications.md
f8 = files[8]
n8_1 = add_node("typography_specifications", "Typography Specifications", "concept", f8)
n8_2 = add_node("font_stack_structure", "Font Stack Structure", "concept", f8)
n8_3 = add_node("type_scale", "Typography Type Scale", "concept", f8)

add_edge(n8_1, n8_2, "references", "EXTRACTED", 1.0, f8)
add_edge(n8_1, n8_3, "references", "EXTRACTED", 1.0, f8)
add_edge(n0_1, n8_1, "references", "EXTRACTED", 1.0, f0)

# 10. brand/references/update.md
f9 = files[9]
n9_1 = add_node("brand_update_workflow", "Brand Update Workflow", "concept", f9)
add_edge(n0_1, n9_1, "references", "EXTRACTED", 1.0, f0)
add_edge(n9_1, n4_1, "references", "EXTRACTED", 1.0, f9)

# 11. brand/references/visual-identity.md
f10 = files[10]
n10_1 = add_node("visual_identity_basics", "Visual Identity Basics", "concept", f10)
add_edge(n0_1, n10_1, "references", "EXTRACTED", 1.0, f0)
add_edge(n10_1, n6_1, "references", "EXTRACTED", 1.0, f10)
add_edge(n10_1, n4_1, "references", "EXTRACTED", 1.0, f10)

# 12. brand/references/voice-framework.md
f11 = files[11]
n11_1 = add_node("voice_framework", "Brand Voice Framework", "concept", f11)
n11_2 = add_node("voice_vs_tone", "Voice vs Tone Distinction", "rationale", f11)

add_edge(n11_1, n11_2, "references", "EXTRACTED", 1.0, f11)
add_edge(n0_1, n11_1, "references", "EXTRACTED", 1.0, f0)

# 13. brand/templates/brand-guidelines-starter.md
f12 = files[12]
n12_1 = add_node("brand_guidelines_starter", "Brand Guidelines Starter Template", "document", f12)
add_edge(n3_1, n12_1, "semantically_similar_to", "INFERRED", 0.95, f12)

# 14. design-system/SKILL.md
f13 = files[13]
n13_1 = add_node("design_system_skill", "Design System Skill System", "concept", f13, author="claudekit")
n13_2 = add_node("three_layer_architecture_overview", "Three-Layer Token Architecture", "rationale", f13, author="claudekit")

add_edge(n13_1, n13_2, "references", "EXTRACTED", 1.0, f13)

# 15. design-system/references/component-specs.md
f14 = files[14]
n14_1 = add_node("component_specifications", "Component Specifications", "concept", f14)
n14_2 = add_node("button_component_spec", "Button Component Spec", "concept", f14)
n14_3 = add_node("input_component_spec", "Input Component Spec", "concept", f14)

add_edge(n14_1, n14_2, "references", "EXTRACTED", 1.0, f14)
add_edge(n14_1, n14_3, "references", "EXTRACTED", 1.0, f14)
add_edge(n13_1, n14_1, "references", "EXTRACTED", 1.0, f13)

# 16. design-system/references/component-tokens.md
f15 = files[15]
n15_1 = add_node("component_tokens", "Component Tokens", "concept", f15)
n15_2 = add_node("button_tokens", "Button Tokens", "concept", f15)

add_edge(n15_1, n15_2, "references", "EXTRACTED", 1.0, f15)
add_edge(n13_1, n15_1, "references", "EXTRACTED", 1.0, f13)

# 17. design-system/references/primitive-tokens.md
f16 = files[16]
n16_1 = add_node("primitive_tokens", "Primitive Tokens", "concept", f16)
n16_2 = add_node("color_scales_primitive", "Color Scales Primitive", "concept", f16)
n16_3 = add_node("spacing_scale_primitive", "Spacing Scale Primitive", "concept", f16)

add_edge(n16_1, n16_2, "references", "EXTRACTED", 1.0, f16)
add_edge(n16_1, n16_3, "references", "EXTRACTED", 1.0, f16)
add_edge(n13_1, n16_1, "references", "EXTRACTED", 1.0, f13)

# 18. design-system/references/semantic-tokens.md
f17 = files[17]
n17_1 = add_node("semantic_tokens", "Semantic Tokens", "concept", f17)
n17_2 = add_node("color_semantics", "Color Semantics", "concept", f17)
n17_3 = add_node("dark_mode_overrides", "Dark Mode Overrides", "concept", f17)

add_edge(n17_1, n17_2, "references", "EXTRACTED", 1.0, f17)
add_edge(n17_1, n17_3, "references", "EXTRACTED", 1.0, f17)
add_edge(n17_1, n16_1, "references", "EXTRACTED", 1.0, f17)
add_edge(n13_1, n17_1, "references", "EXTRACTED", 1.0, f13)

# 19. design-system/references/states-and-variants.md
f18 = files[18]
n18_1 = add_node("states_and_variants", "States and Variants Guide", "concept", f18)
n18_2 = add_node("interactive_states_definition", "Interactive States Definition", "concept", f18)
n18_3 = add_node("focus_ring_spec", "Focus Ring Specification", "concept", f18)

add_edge(n18_1, n18_2, "references", "EXTRACTED", 1.0, f18)
add_edge(n18_1, n18_3, "references", "EXTRACTED", 1.0, f18)
add_edge(n13_1, n18_1, "references", "EXTRACTED", 1.0, f13)

# 20. design-system/references/tailwind-integration.md
f19 = files[19]
n19_1 = add_node("tailwind_integration", "Tailwind CSS Integration", "concept", f19)
n19_2 = add_node("hsl_format_benefits", "HSL Format Benefits", "rationale", f19)
n19_3 = add_node("shadcn_ui_alignment", "shadcn/ui Alignment", "concept", f19)

add_edge(n19_1, n19_2, "rationale_for", "EXTRACTED", 1.0, f19)
add_edge(n19_1, n19_3, "references", "EXTRACTED", 1.0, f19)
add_edge(n19_1, n17_1, "references", "EXTRACTED", 1.0, f19)
add_edge(n13_1, n19_1, "references", "EXTRACTED", 1.0, f13)

# 21. design-system/references/token-architecture.md
f20 = files[20]
n20_1 = add_node("token_architecture_guide", "Token Architecture Deep Dive", "rationale", f20)
n20_2 = add_node("why_three_layers", "Why Three Layers Decision Rationale", "rationale", f20)

add_edge(n20_1, n20_2, "rationale_for", "EXTRACTED", 1.0, f20)
add_edge(n20_1, n16_1, "references", "EXTRACTED", 1.0, f20)
add_edge(n20_1, n17_1, "references", "EXTRACTED", 1.0, f20)
add_edge(n20_1, n15_1, "references", "EXTRACTED", 1.0, f20)
add_edge(n15_1, n17_1, "references", "EXTRACTED", 1.0, f15)
add_edge(n13_1, n20_1, "references", "EXTRACTED", 1.0, f13)

# 22. design/SKILL.md
f21 = files[21]
n21_1 = add_node("design_master_skill", "Design Master Orchestrator Skill", "concept", f21, author="claudekit")
n21_2 = add_node("logo_design_builtin", "Logo Design Workflow", "concept", f21, author="claudekit")
n21_3 = add_node("cip_design_builtin", "Corporate Identity Program (CIP) Workflow", "concept", f21, author="claudekit")

add_edge(n21_1, n21_2, "references", "EXTRACTED", 1.0, f21)
add_edge(n21_1, n21_3, "references", "EXTRACTED", 1.0, f21)
add_edge(n21_1, n0_1, "references", "EXTRACTED", 1.0, f21)
add_edge(n21_1, n13_1, "references", "EXTRACTED", 1.0, f21)

# Semantic similarities (cross-cutting)
add_edge(n4_2, n16_2, "semantically_similar_to", "INFERRED", 0.85, f4)
add_edge(n8_2, n16_1, "semantically_similar_to", "INFERRED", 0.75, f8)

# Hyperedges (max 3)
add_hyperedge("three_layer_token_system", "Three-Layer Token System Architecture", [n16_1, n17_1, n15_1], "form", "EXTRACTED", 1.0, f20)
add_hyperedge("brand_identity_governance", "Brand Governance Ecosystem", [n10_1, n11_1, n7_1, n5_1], "participate_in", "INFERRED", 0.85, f0)
add_hyperedge("design_skills_hierarchy", "Design Skills System Hierarchy", [n21_1, n0_1, n13_1], "participate_in", "EXTRACTED", 1.0, f21)

output_data = {
    "nodes": nodes,
    "edges": edges,
    "hyperedges": hyperedges,
    "input_tokens": 0,
    "output_tokens": 0
}

out_path = '/home/hossein/Desktop/projects/mehdi/building-management/graphify-out/.graphify_chunk_04.json'
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, 'w', encoding='utf-8') as out_f:
    json.dump(output_data, out_f, indent=2)

print("Generated successfully!")
print(f"Nodes: {len(nodes)}")
print(f"Edges: {len(edges)}")
print(f"Hyperedges: {len(hyperedges)}")
