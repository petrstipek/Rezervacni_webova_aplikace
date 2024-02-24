--==============================================================
-- DBMS name:      ANSI Level 2
-- Created on:     18.02.2024 11:34:20
--==============================================================


--drop index Dostupne_hodiny_PK;

--drop index Instruktor_PK;

--drop index Klient_PK;

--drop index Osoba_PK;

--drop index Rezervace_PK;

--drop index ma_vytvorenu_FK;

--drop index Spravce_skoly_PK;

--drop index je_soucasti_FK;

--drop index ma_vypsane2_FK;

--drop index ma_vypsane_FK;

--drop index ma_vypsane_PK;

--drop index ma_vyuku2_FK;

--drop index ma_vyuku_FK;

--drop index ma_vyuku_PK;

--drop index prirazeno2_FK;

--drop index prirazeno_FK;

--drop index prirazeno_PK;

--drop table Zak cascade;

--drop table prirazeno cascade;

--drop table ma_vyuku cascade;

--drop table Rezervace cascade;

--drop table ma_vypsane cascade;

--drop table Klient cascade;

--drop table Instruktor cascade;

--drop table Spravce_skoly cascade;

--drop table Osoba cascade;

--drop table Dostupne_hodiny cascade;

--==============================================================
-- Table: Dostupne_hodiny
--==============================================================
create table Dostupne_hodiny (
ID_hodiny            INTEGER              not null,
datum                DATE                 not null,
cas_zacatku          TIME                 not null,
stav                 VARCHAR(10)          not null,
typ_hodiny           VARCHAR(30)          not null,
obsazenost           INTEGER,
kapacita             INTEGER,
primary key (ID_hodiny)
);

--==============================================================
-- Index: Dostupne_hodiny_PK
--==============================================================
create unique index Dostupne_hodiny_PK on Dostupne_hodiny (
ID_hodiny ASC
);

--==============================================================
-- Table: Osoba
--==============================================================
create table Osoba (
ID_osoba             INTEGER              not null,
jmeno                VARCHAR(20)          not null,
prijmeni             VARCHAR(30)          not null,
email                VARCHAR(30)          not null,
tel_cislo            VARCHAR(15)          not null,
prihl_jmeno          VARCHAR(20),
heslo                VARCHAR(20),
primary key (ID_osoba)
);

--==============================================================
-- Index: Osoba_PK
--==============================================================
create unique index Osoba_PK on Osoba (
ID_osoba ASC
);

--==============================================================
-- Table: Spravce_skoly
--==============================================================
create table Spravce_skoly (
ID_osoba             INTEGER              not null,
jmeno                VARCHAR(20)          not null,
prijmeni             VARCHAR(30)          not null,
email                VARCHAR(30)          not null,
tel_cislo            VARCHAR(15)          not null,
prihl_jmeno          VARCHAR(20),
heslo                VARCHAR(20),
primary key (ID_osoba),
foreign key (ID_osoba)
      references Osoba (ID_osoba)
);

--==============================================================
-- Index: Spravce_skoly_PK
--==============================================================
create unique index Spravce_skoly_PK on Spravce_skoly (
ID_osoba ASC
);

--==============================================================
-- Table: Instruktor
--==============================================================
create table Instruktor (
ID_osoba             INTEGER              not null,
jmeno                VARCHAR(20)          not null,
prijmeni             VARCHAR(30)          not null,
email                VARCHAR(30)          not null,
tel_cislo            VARCHAR(15)          not null,
prihl_jmeno          VARCHAR(20),
heslo                VARCHAR(20),
seniorita            VARCHAR(10)          not null,
datum_narozeni       DATE                 not null,
datum_nastupu        DATE                 not null,
primary key (ID_osoba),
foreign key (ID_osoba)
      references Osoba (ID_osoba)
);

--==============================================================
-- Index: Instruktor_PK
--==============================================================
create unique index Instruktor_PK on Instruktor (
ID_osoba ASC
);

--==============================================================
-- Table: Klient
--==============================================================
create table Klient (
ID_osoba             INTEGER              not null,
jmeno                VARCHAR(20)          not null,
prijmeni             VARCHAR(30)          not null,
email                VARCHAR(30)          not null,
tel_cislo            VARCHAR(15)          not null,
prihl_jmeno          VARCHAR(20),
heslo                VARCHAR(20),
primary key (ID_osoba),
foreign key (ID_osoba)
      references Osoba (ID_osoba)
);

--==============================================================
-- Index: Klient_PK
--==============================================================
create unique index Klient_PK on Klient (
ID_osoba ASC
);

--==============================================================
-- Table: ma_vypsane
--==============================================================
create table ma_vypsane (
ID_osoba             INTEGER              not null,
ID_hodiny            INTEGER              not null,
primary key (ID_osoba, ID_hodiny),
foreign key (ID_osoba)
      references Instruktor (ID_osoba),
foreign key (ID_hodiny)
      references Dostupne_hodiny (ID_hodiny)
);

--==============================================================
-- Index: ma_vypsane_PK
--==============================================================
create unique index ma_vypsane_PK on ma_vypsane (
ID_osoba ASC,
ID_hodiny ASC
);

--==============================================================
-- Index: ma_vypsane_FK
--==============================================================
create  index ma_vypsane_FK on ma_vypsane (
ID_osoba ASC
);

--==============================================================
-- Index: ma_vypsane2_FK
--==============================================================
create  index ma_vypsane2_FK on ma_vypsane (
ID_hodiny ASC
);

--==============================================================
-- Table: Rezervace
--==============================================================
create table Rezervace (
ID_rezervace         INTEGER              not null,
ID_osoba             INTEGER              not null,
typ_rezervace        VARCHAR(20)          not null,
termin               DATE                 not null,
cas_zacatku          TIME                 not null,   
doba_vyuky           INTEGER              not null,
jazyk                VARCHAR(20)          not null,
pocet_zaku           INTEGER              not null,
platba               VARCHAR(20)          not null,
poznamka             VARCHAR(100),
primary key (ID_rezervace),
foreign key (ID_osoba)
      references Klient (ID_osoba)
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
ID_osoba ASC
);

--==============================================================
-- Table: ma_vyuku
--==============================================================
create table ma_vyuku (
ID_osoba             INTEGER              not null,
ID_rezervace         INTEGER              not null,
primary key (ID_osoba, ID_rezervace),
foreign key (ID_osoba)
      references Instruktor (ID_osoba),
foreign key (ID_rezervace)
      references Rezervace (ID_rezervace)
);

--==============================================================
-- Index: ma_vyuku_PK
--==============================================================
create unique index ma_vyuku_PK on ma_vyuku (
ID_osoba ASC,
ID_rezervace ASC
);

--==============================================================
-- Index: ma_vyuku_FK
--==============================================================
create  index ma_vyuku_FK on ma_vyuku (
ID_osoba ASC
);

--==============================================================
-- Index: ma_vyuku2_FK
--==============================================================
create  index ma_vyuku2_FK on ma_vyuku (
ID_rezervace ASC
);

--==============================================================
-- Table: prirazeno
--==============================================================
create table prirazeno (
ID_rezervace         INTEGER              not null,
ID_hodiny            INTEGER              not null,
primary key (ID_rezervace, ID_hodiny),
foreign key (ID_rezervace)
      references Rezervace (ID_rezervace),
foreign key (ID_hodiny)
      references Dostupne_hodiny (ID_hodiny)
);

--==============================================================
-- Index: prirazeno_PK
--==============================================================
create unique index prirazeno_PK on prirazeno (
ID_rezervace ASC,
ID_hodiny ASC
);

--==============================================================
-- Index: prirazeno_FK
--==============================================================
create  index prirazeno_FK on prirazeno (
ID_rezervace ASC
);

--==============================================================
-- Index: prirazeno2_FK
--==============================================================
create  index prirazeno2_FK on prirazeno (
ID_hodiny ASC
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

