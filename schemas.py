from marshmallow import Schema, fields


class PlainCourseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    subject_type = fields.Str(required=True)
    test_providers = fields.Str(required=False, default="no providers")  # TODO: replace with list postgress
    summary = fields.Str(required=False, default="no summary provided")


class PlainStudentSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    age = fields.Int(required=True)
    summary = fields.Str(required=False, default="no summary provided")
    profile_picture = fields.Raw(type="file", required=False)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class PlainTutorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    age = fields.Int(required=True)
    summary = fields.Str(required=False, default="no summary provided")
    profile_picture = fields.Raw(type="file", required=False)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class PlainCourseRegisterSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)


class StudentSchema(PlainStudentSchema):
    # courses = fields.List(fields.Nested(PlainCourseSchema(), dump_only=True))
    registers = fields.List(fields.Nested(PlainCourseRegisterSchema(), dump_only=True))
    # tutors = fields.List(fields.Nested(PlainTutorSchema(), dump_only=True))


class TutorSchema(PlainTutorSchema):
    # students = fields.List(fields.Nested(PlainStudentSchema(), dump_only=True))
    registers = fields.List(fields.Nested(PlainCourseRegisterSchema(), dump_only=True))
    # courses = fields.List(fields.Nested(PlainCourseSchema(), dump_only=True))


class CourseSchema(PlainCourseSchema):
    students = fields.List(fields.Nested(PlainStudentSchema(), dump_only=True))
    registers = fields.List(fields.Nested(PlainCourseRegisterSchema(), dump_only=True))
    # tutors = fields.List(fields.Nested(PlainTutorSchema(), dump_only=True))


class CourseRegisterSchema(PlainCourseRegisterSchema):
    course_id = fields.Int(load_only=True)
    course = fields.Nested(PlainCourseSchema(), dump_only=True)
    students = fields.List(fields.Nested(PlainStudentSchema(), dump_only=True))
    tutors = fields.List(fields.Nested(PlainTutorSchema(), dump_only=True))


class FileUploadSchema(Schema):
    user_type = fields.Str(required=True)
    uid = fields.Int(required=True)
    file = fields.Raw(type="file")


class CourseRegisterAndStudentSchema(Schema):
    message = fields.Str()
    course_register = fields.Nested(CourseRegisterSchema())
    student = fields.Nested(StudentSchema())


class CourseRegisterAndTutorSchema(Schema):
    message = fields.Str()
    course_register = fields.Nested(CourseRegisterSchema())
    tutor = fields.Nested(TutorSchema())


class StudentUpdateSchema(Schema):
    name = fields.Str()
    email = fields.Email()
    age = fields.Int()
    summary = fields.Str()
    profile_picture = fields.Raw(type="file")


class TutorUpdateSchema(Schema):
    name = fields.Str()
    email = fields.Email()
    age = fields.Int()
    summary = fields.Str()
    profile_picture = fields.Raw(type="file")


class CourseUpdateSchema(Schema):
    name = fields.Str()
    subject_type = fields.Str()
    test_providers = fields.List(fields.Str)
    tutors = fields.Int()
    summary = fields.Str()


class LoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)


class CourseRegisterUpdateSchema(Schema):
    course_id = fields.Int()
    students = fields.Int()
