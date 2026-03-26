from bson import ObjectId


def is_valid_object_id(value: str | None) -> bool:
    return bool(value) and ObjectId.is_valid(value)


def as_object_id(value: str) -> ObjectId:
    return ObjectId(value)
