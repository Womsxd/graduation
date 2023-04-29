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
