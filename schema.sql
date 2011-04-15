drop table if exists tweets;
drop table if exists settings;

create table tweets (
    id primary key,
    dt date not null,
    user varchar not null,
    image varchar not null,
    text varchar not null,
    approved not null default 0
);

create table settings (
    key primary key,
    value
);
