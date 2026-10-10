def validate_citations(llm_citations, evidence_pack):
    valid = []
    authorized_source_ids = {ev["source_id"] for ev in evidence_pack}
    
    for citation in llm_citations:
        if citation in authorized_source_ids:
            valid.append(citation)
            
    return valid
