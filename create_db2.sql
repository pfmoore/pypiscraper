create table packages (
    package text,
    json text
);

create table releases (
    package text,
    version text,
    hidden integer,
    json text
);
