def key_from_name(named_entity):
    t = named_entity.get("deviceTypeName", None)
    n = named_entity.get("deviceItemName", None)
    if t is None or n is None:
        return None
    return t + " : " + n

def get_parent(xref_entities, named_entity):
    containedIn = named_entity.get("containedIn", {})
    key = key_from_name(containedIn)
    if key is None:
        return None
    return xref_entities.get(key, None)

def get_attrs(entity):
    return [x for x in entity.get("attributes", []) if x.get("name", None) is not None]

def fill_properties_by_contained(entities):

    xref_entities = {key_from_name(e): e for e in entities if key_from_name(e) is not None}

    for entity in entities:
        entity_attrs = get_attrs(entity)

        parent = get_parent(xref_entities, entity)
        while parent is not None:
            parent_attrs = get_attrs(parent)
            for pa in parent_attrs:
                found = [ea for ea in entity_attrs if pa["name"] == ea["name"]]
                if len(found) == 0:
                    entity_attrs.append(pa)

            parent = get_parent(xref_entities, parent)

        entity["attributes"] = entity_attrs