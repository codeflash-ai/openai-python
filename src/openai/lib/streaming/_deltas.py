from __future__ import annotations


def accumulate_delta(acc: dict[object, object], delta: dict[object, object]) -> dict[object, object]:
    dict_type = dict
    list_type = list
    str_type = str
    num_types = (int, float)
    simple_types = (str, int, float)
    index_type_keys = ("index", "type")

    for key, delta_value in delta.items():
        # Fast path: Key not in accumulator
        if key not in acc:
            acc[key] = delta_value
            continue

        acc_value = acc[key]
        if acc_value is None:
            acc[key] = delta_value
            continue

        # `index` or `type` should not be accumulated
        if key in index_type_keys:
            acc[key] = delta_value
            continue

        acc_type = type(acc_value)
        delta_type = type(delta_value)

        if acc_type is str_type and delta_type is str_type:
            acc_value += delta_value
        elif acc_type in num_types and delta_type in num_types:
            acc_value += delta_value
        # Inline isinstance, avoid helper call overhead
        elif acc_type is dict_type and delta_type is dict_type:
            acc_value = accumulate_delta(acc_value, delta_value)
        elif acc_type is list_type and delta_type is list_type:
            # Speed up: check type of first element only if present
            # If all elements are simple types, batch extend
            if acc_value:
                first_simple_type = all(isinstance(x, simple_types) for x in acc_value)
            else:
                first_simple_type = True  # Empty lists are extendable

            if first_simple_type:
                acc_value.extend(delta_value)
                continue

            # Keep the logic in the original order for dicts in lists
            for delta_entry in delta_value:
                if not isinstance(delta_entry, dict_type):
                    raise TypeError(f"Unexpected list delta entry is not a dictionary: {delta_entry}")

                try:
                    index = delta_entry["index"]
                except KeyError as exc:
                    raise RuntimeError(f"Expected list delta entry to have an `index` key; {delta_entry}") from exc

                if not isinstance(index, int):
                    raise TypeError(f"Unexpected, list delta entry `index` value is not an integer; {index}")

                try:
                    acc_entry = acc_value[index]
                except IndexError:
                    acc_value.insert(index, delta_entry)
                else:
                    if not isinstance(acc_entry, dict_type):
                        raise TypeError("not handled yet")
                    acc_value[index] = accumulate_delta(acc_entry, delta_entry)

        acc[key] = acc_value

    return acc
