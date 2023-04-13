from marshmallow import Schema, fields


class CourseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    subject_type = fields.Str(required=True)
    test_providers = fields.Str(required=False, default="no providers")  # TODO: replace with list postgress
    tutors = fields.Int(required=False, default=0)
    summary = fields.Str(required=False, default="no summary provided")


class CourseUpdateSchema(Schema):
    name = fields.Str()
    subject_type = fields.Str()
    test_providers = fields.List(fields.Str)
    tutors = fields.Int()
    summary = fields.Str()


class StudentSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    age = fields.Int(required=True)
    summary = fields.Str(required=False, default="no summary provided")


class StudentUpdateSchema(Schema):
    name = fields.Str()
    email = fields.Email()
    age = fields.Int()
    summary = fields.Str()


class TutorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    age = fields.Int(required=True)
    summary = fields.Str(required=False, default="no summary provided")


class TutorUpdateSchema(Schema):
    name = fields.Str()
    email = fields.Email()
    age = fields.Int()
    summary = fields.Str()


class CourseRegisterSchema(Schema):
    id = fields.Int(dump_only=True)
    course_id = fields.Int(required=True)
    student_ids = fields.Int(required=True)  # TODO: replace with list with postgress


class CourseRegisterUpdateSchema(Schema):
    course_id = fields.Int()
    students = fields.Int()
