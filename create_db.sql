create table last_serial (
    latest integer
);

insert into last_serial values (0);

create table packages (
    package text,
    updated_serial number
);

create table releases (
    package text,
    version text,
    hidden integer
);

create table metadata (
    package text,
    version text,
    stable_version text,
    author text,
    author_email text,
    maintainer text,
    maintainer_email text,
    home_page text,
    license text,
    summary text,
    description text,
    keywords text,
    platform text,
    download_url text,
    requires text,
    requires_dist text,
    provides text,
    provides_dist text,
    requires_external text,
    requires_python text,
    obsoletes text,
    obsoletes_dist text,
    project_url text,
    docs_url text
);

create table classifiers (
    package text,
    version text,
    classifier text
);

create table urls (
    package text,
    version text,
    url text,
    packagetype text,
    filename text,
    size text,
    md5_digest text,
    downloads text,
    has_sig text,
    python_version text,
    comment_text text
);
