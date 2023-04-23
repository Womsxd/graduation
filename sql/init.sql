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
    college_id INTEGER
        references college
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
    inherit TEXT
);

create table student
(
    id       INTEGER not null
        primary key autoincrement,
    sid      TEXT    not null,
    name     TEXT    not null,
    sex      INTEGER default 1 not null,
    class_id INTEGER not null
        references class
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
        references student (sid),
    sessions_id INTEGER not null
        references examsessions,
    subject_id  INTEGER not null
        references subject,
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
    csrf     TEXT
);

create unique index user_account_uindex
    on user (account);

create unique index user_csrf_uindex
    on user (csrf);

