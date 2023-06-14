from marshmallow import Schema, fields


class APIFeatureSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    type = fields.Str()


class APIFeatureStateSchema(Schema):
    feature = fields.Nested(APIFeatureSchema)
    enabled = fields.Bool()
    feature_state_value = fields.Field(allow_none=True)
