def rearrange_sections(payload, sequence):
    reordered_payload = {}
    for section_key, order in sequence.items():
        if section_key in payload:
            section = {subkey: payload[section_key].get(subkey, None) for subkey in order if
                       subkey in payload[section_key]}
            reordered_payload[section_key] = section
    return reordered_payload


def format_payload_seq(dict_sequence, new_payload):
    background_sequence = dict_sequence["backgroundKeys"]
    detailed_description_sequence = dict_sequence["detailedDescriptionKeys"]

    reordered_background = rearrange_sections(new_payload, {"background": background_sequence})
    reordered_detailed_description = rearrange_sections(new_payload,
                                                        {"detailed-description": detailed_description_sequence})

    new_payload["background"] = reordered_background.get("background", {})
    new_payload["detailed-description"] = reordered_detailed_description.get("detailed-description", {})

    return new_payload


def remove_empty_keys(payload):
    if isinstance(payload, dict):
        return {k: remove_empty_keys(v) for k, v in payload.items() if v}
    return payload
