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
            on delete set default
);

create table examsessions
(
    id   INTEGER not null
        primary key autoincrement,
    name TEXT
);

create table groups
(
    id      INTEGER not null
        primary key autoincrement,
    name    TEXT    not null,
    inherit INTEGER
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
    result      REAL    not null
);

create table user
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
    otp_act_exp_time INTEGER

);

create unique index user_account_uindex
    on user (account);

create unique index user_csrf_uindex
    on user (csrf);

create unique index user_otp_secret_uindex
    on user (otp_secret);
