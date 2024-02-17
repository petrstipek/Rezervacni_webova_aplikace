--==============================================================
-- DBMS name:      ANSI Level 2
-- Created on:     17.02.2024 10:56:40
--==============================================================

drop index Dostupne_hodiny_PK;

drop index prirazeno_FK;

drop index Instruktor_PK;

drop index Klient_PK;

drop index Osoba_PK;

drop index Rezervace_PK;

drop index ma_vytvorenu_FK;

drop index Spravce_skoly_PK;

drop index je_soucasti_FK;

drop index ma_vypsane2_FK;

drop index ma_vypsane_FK;

drop index ma_vypsane_PK;

drop index ma_vyuku2_FK;

drop index ma_vyuku_FK;

drop index ma_vyuku_PK;

drop table ma_vypsane cascade;

drop table Dostupne_hodiny cascade;

drop table ma_vyuku cascade;

drop table Zak cascade;

drop table Instruktor cascade;

drop table Rezervace cascade;

drop table Klient cascade;

drop table Spravce_skoly cascade;

drop table Osoba cascade;

--==============================================================
-- Table: Osoba
--==============================================================
create table Osoba (
ID_ososba            INTEGER              not null,
jmeno                VARCHAR(20)          not null,
prijmeni             VARCHAR(30)          not null,
email                VARCHAR(30)          not null,
tel_cislo            VARCHAR(15)          not null,
prihl_jmeno          VARCHAR(20),
heslo                VARCHAR(20),
primary key (ID_ososba)
);

--==============================================================
-- Index: Osoba_PK
--==============================================================
create unique index Osoba_PK on Osoba (
ID_ososba ASC
);

--==============================================================
-- Table: Spravce_skoly
--==============================================================
create table Spravce_skoly (
ID_ososba            INTEGER              not null,
jmeno                VARCHAR(20)          not null,
prijmeni             VARCHAR(30)          not null,
email                VARCHAR(30)          not null,
tel_cislo            VARCHAR(15)          not null,
prihl_jmeno          VARCHAR(20),
heslo                VARCHAR(20),
primary key (ID_ososba),
foreign key (ID_ososba)
    references Osoba (ID_ososba)
);

--==============================================================
-- Index: Spravce_skoly_PK
--==============================================================
create unique index Spravce_skoly_PK on Spravce_skoly (
ID_ososba ASC
);

--==============================================================
-- Table: Klient
--==============================================================
create table Klient (
ID_ososba            INTEGER              not null,
jmeno                VARCHAR(20)          not null,
prijmeni             VARCHAR(30)          not null,
email                VARCHAR(30)          not null,
tel_cislo            VARCHAR(15)          not null,
prihl_jmeno          VARCHAR(20),
heslo                VARCHAR(20),
primary key (ID_ososba),
foreign key (ID_ososba)
    references Osoba (ID_ososba)
);

--==============================================================
-- Index: Klient_PK
--==============================================================
create unique index Klient_PK on Klient (
ID_ososba ASC
);

--==============================================================
-- Table: Rezervace
--==============================================================
create table Rezervace (
ID_rezervace         INTEGER              not null,
ID_ososba            INTEGER              not null,
typ_rezervace        VARCHAR(20)          not null,
termin               DATE                 not null,
typ_vyuky            VARCHAR(20)          not null,
jazyk                VARCHAR(20)          not null,
pocet_zaku           INTEGER              not null,
poznamka             VARCHAR(100),
primary key (ID_rezervace),
foreign key (ID_ososba)
    references Klient (ID_ososba)
);

--==============================================================
-- Index: Rezervace_PK
--==============================================================
create unique index Rezervace_PK on Rezervace (
ID_rezervace ASC
);

--==============================================================
-- Index: ma_vytvorenu_FK
--==============================================================
create  index ma_vytvorenu_FK on Rezervace (
ID_ososba ASC
);

--==============================================================
-- Table: Instruktor
--==============================================================
create table Instruktor (
ID_ososba            INTEGER              not null,
jmeno                VARCHAR(20)          not null,
prijmeni             VARCHAR(30)          not null,
email                VARCHAR(30)          not null,
tel_cislo            VARCHAR(15)          not null,
prihl_jmeno          VARCHAR(20),
heslo                VARCHAR(20),
seniorita            VARCHAR(10)          not null,
datum_narozeni       DATE                 not null,
datum_nastupu        DATE                 not null,
primary key (ID_ososba),
foreign key (ID_ososba)
    references Osoba (ID_ososba)
);

--==============================================================
-- Index: Instruktor_PK
--==============================================================
create unique index Instruktor_PK on Instruktor (
ID_ososba ASC
);

--==============================================================
-- Table: Zak
--==============================================================
create table Zak (
ID_rezervace         INTEGER              not null,
jmeno                VARCHAR(20)          not null,
prijmeni             VARCHAR(30)          not null,
zkusenost            VARCHAR(20)          not null,
vek                  INTEGER              not null,
foreign key (ID_rezervace)
    references Rezervace (ID_rezervace)
);

--==============================================================
-- Index: je_soucasti_FK
--==============================================================
create  index je_soucasti_FK on Zak (
ID_rezervace ASC
);

--==============================================================
-- Table: ma_vyuku
--==============================================================
create table ma_vyuku (
ID_ososba            INTEGER              not null,
ID_rezervace         INTEGER              not null,
primary key (ID_ososba, ID_rezervace),
foreign key (ID_ososba)
    references Instruktor (ID_ososba),
foreign key (ID_rezervace)
    references Rezervace (ID_rezervace)
);

--==============================================================
-- Index: ma_vyuku_PK
--==============================================================
create unique index ma_vyuku_PK on ma_vyuku (
ID_ososba ASC,
ID_rezervace ASC
);

--==============================================================
-- Index: ma_vyuku_FK
--==============================================================
create  index ma_vyuku_FK on ma_vyuku (
ID_ososba ASC
);

--==============================================================
-- Index: ma_vyuku2_FK
--==============================================================
create  index ma_vyuku2_FK on ma_vyuku (
ID_rezervace ASC
);

--==============================================================
-- Table: Dostupne_hodiny
--==============================================================
create table Dostupne_hodiny (
ID_hodiny            INTEGER              not null,
ID_rezervace         INTEGER              not null,
datum                DATE,
cas_zacatku          TIME,
stav                 VARCHAR(10),
primary key (ID_hodiny),
foreign key (ID_rezervace)
    references Rezervace (ID_rezervace)
);

--==============================================================
-- Index: Dostupne_hodiny_PK
--==============================================================
create unique index Dostupne_hodiny_PK on Dostupne_hodiny (
ID_hodiny ASC
);

--==============================================================
-- Index: prirazeno_FK
--==============================================================
create  index prirazeno_FK on Dostupne_hodiny (
ID_rezervace ASC
);

--==============================================================
-- Table: ma_vypsane
--==============================================================
create table ma_vypsane (
ID_ososba            INTEGER              not null,
ID_hodiny            INTEGER              not null,
primary key (ID_ososba, ID_hodiny),
foreign key (ID_ososba)
    references Instruktor (ID_ososba),
foreign key (ID_hodiny)
    references Dostupne_hodiny (ID_hodiny)
);

--==============================================================
-- Index: ma_vypsane_PK
--==============================================================
create unique index ma_vypsane_PK on ma_vypsane (
ID_ososba ASC,
ID_hodiny ASC
);

--==============================================================
-- Index: ma_vypsane_FK
--==============================================================
create  index ma_vypsane_FK on ma_vypsane (
ID_ososba ASC
);

--==============================================================
-- Index: ma_vypsane2_FK
--==============================================================
create  index ma_vypsane2_FK on ma_vypsane (
ID_hodiny ASC
);

