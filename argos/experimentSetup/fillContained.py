from copy import deepcopy


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


def spread_attributes(entity):
    if "location" in entity:
        loc = entity["location"]
        entity["MapName"] = loc["name"]
        entity["Latitude"] = loc["coordinates"][0]
        entity["Longitude"] = loc["coordinates"][1]
        del entity["location"]
    if "attributes" in entity:
        entity_attrs = get_attrs(entity)
        for attr in entity_attrs:
            entity[attr["name"]] = attr["value"]
        del entity["attributes"]

def handle_String(value):
    return value

def handle_Number(value):
    return float(value)



def fill_properties_by_contained(entities_types_dict, meta_entities):

    handlerDict = dict(Number=handle_Number,
                       String=handle_String)

    xref_entities = {key_from_name(e): e for e in meta_entities if key_from_name(e) is not None}

    filled_entities = deepcopy(meta_entities)
    for entity in filled_entities:
        if key_from_name(entity) is not None:
            device_type = entities_types_dict[entity["deviceTypeName"]]
            type_attrs = device_type._metadata.get("attributeTypes", [])
            attrs_names = [a.get("name", None) for a in type_attrs]
            attrs_names = [a for a in attrs_names if a is not None]
            type_attrs_dict = dict((x['name'],x['type']) for x in type_attrs)

            entity_attrs = get_attrs(entity)
            for singleEntityAttrs in entity_attrs:
                entityName = singleEntityAttrs['name']
                singleEntityAttrs['value'] = handlerDict[type_attrs_dict[entityName]](singleEntityAttrs['value'])


            parent = get_parent(xref_entities, entity)
            while parent is not None:
                parent_attrs = get_attrs(parent)
                for pa in parent_attrs:
                    pa_name = pa["name"]
                    if pa_name in attrs_names:
                        found = [ea for ea in entity_attrs if pa_name == ea["name"]]
                        if len(found) == 0:
                            entity_attrs.append(pa)

                parent = get_parent(xref_entities, parent)

            entity["attributes"] = entity_attrs

    for entity in filled_entities:
        if "containedIn" in entity:
            del entity["containedIn"]
        spread_attributes(entity)

    return filled_entities
