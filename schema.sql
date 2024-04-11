create table user_data
(
    User_ID       int auto_increment
        primary key,
    Username      varchar(40) not null,
    Email_address varchar(40) null,
    Full_name     varchar(40) not null,
    Password      varchar(40) not null,
    Account_type  varchar(40) not null
);

create table question_papers
(
    QPaper_ID          int auto_increment
        primary key,
    User_ID            int          not null,
    Show_responce      varchar(40)  null,
    Accepting_responce varchar(40)  not null,
    Rooms_accepted     varchar(40)  not null,
    Title              varchar(50)  not null,
    Description        varchar(500) not null,
    Limit_response     varchar(40)  null,
    constraint question_papers_ibfk_1
        foreign key (User_ID) references user_data (User_ID)
);

create index User_ID
    on question_papers (User_ID);

create table questions
(
    Ques_ID     int auto_increment
        primary key,
    QPaper_ID   int          not null,
    QType       varchar(30)  not null,
    Question    varchar(500) not null,
    Options     varchar(500) null,
    Correct_ans int          null,
    MinRange    varchar(30)  null,
    MaxRange    varchar(30)  null,
    constraint questions_ibfk_1
        foreign key (QPaper_ID) references question_papers (QPaper_ID)
);

create index QPaper_ID
    on questions (QPaper_ID);

create table rooms_and_forms
(
    QPaper_ID int          not null,
    Room_ID   int          not null,
    Room_Name varchar(100) null,
    constraint rooms_and_forms_ibfk_1
        foreign key (QPaper_ID) references question_papers (QPaper_ID)
);

create index QPaper_ID
    on rooms_and_forms (QPaper_ID);

create table rooms_info
(
    Room_ID   int auto_increment
        primary key,
    User_ID   int          not null,
    Room_Name varchar(100) null,
    constraint rooms_info_ibfk_1
        foreign key (User_ID) references user_data (User_ID)
);

create index User_ID
    on rooms_info (User_ID);

