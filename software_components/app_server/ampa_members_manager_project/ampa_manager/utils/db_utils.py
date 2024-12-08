def distinct_count(queryset, field_name='id'):
    values = []
    for obj in queryset.all():
        value = getattr(obj, field_name)
        if value not in values:
            values.append(value)
    return len(values)
