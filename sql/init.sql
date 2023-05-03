create table college
(
    id   INTEGER not null
        primary key autoincrement,
    name TEXT    not null
);

create table class
(
    id         INTEGER not null
        primary key autoincrement,
    name       TEXT    not null,
    college_id INTEGER default 1 not null
        references college
            on delete set default,
    grade      INTEGER default 0 not null
);

create table examsessions
(
    id   INTEGER not null
        primary key autoincrement,
    name TEXT
);

create table groups
(
    id          INTEGER not null
        primary key autoincrement,
    name        TEXT    not null,
    permissions TEXT,
    inherit     TEXT
);

create table student
(
    id       INTEGER not null
        primary key autoincrement,
    sid      TEXT    not null,
    name     TEXT    not null,
    sex      INTEGER default 1 not null,
    class_id INTEGER default 1 not null
        references class
            on delete set default
);

create unique index student_sid_uindex
    on student (sid);

create table subject
(
    id   INTEGER not null
        primary key autoincrement,
    name TEXT    not null
);

create table examinfo
(
    id          INTEGER not null
        primary key autoincrement,
    sid         TEXT    not null
        references student (sid)
            on delete cascade,
    sessions_id INTEGER default 1 not null
        references examsessions
            on delete set default,
    subject_id  INTEGER default 1 not null
        references subject
            on delete set default,
    result      REAL    default 0 not null
);

create table users
(
    id       INTEGER not null
        primary key autoincrement,
    account  TEXT    not null,
    password TEXT    not null,
    group_id INTEGER default 3 not null
        references groups,
    csrf     TEXT,
    otp_status       INT     default 0,
    otp_secret         TEXT,
    otp_act_exp_time INTEGER,
    banned INT default 0 not null

);

create unique index users_account_uindex
    on users (account);

create unique index users_csrf_uindex
    on users (csrf);

create unique index users_otp_secret_uindex
    on users (otp_secret);

-- 创建默认内容
insert into college values (1,'默认学院');
insert into subject values (1,'默认科目');
insert into examsessions values (1,'默认考试');
-- 这里白班机要学院创完事才能
insert into class values  (1,'默认班级',1,0);
-- 默认权限组
insert into groups values (1, 'admin', '*', null);
insert into groups values (2, 'user', 'exam.info.*,exam.session.list,exam.session.query,school.college.list,school.college.query,school.class.list,school.class.query,student.edit,student.list,student.query,subject.list,subject.query', null);
insert into groups values (3, 'guest', null, null);
-- 默认用户名称和密码都是admin
insert into users values (1, 'admin', 'pbkdf2:sha512:260000$ITYGGnyeryw0UsjC$22201dbf5c656a34da05b739266026ab212bc5b1c13a5d39770ad29cbd62ac6070025cc4c1c214e22952383bcf0214add573ea8988949a3d7e4833706202a6da', 1, null, 0, null, null, 0);