use db;

CREATE TABLE vacancies(
    VacancyID int not null AUTO_INCREMENT,
    VacancyTitle varchar(64) NOT NULL,
    Experience varchar(64) NOT NULL,
    JobCreator varchar(128) NOT NULL,
    Adress varchar(128) NOT NULL,
    PRIMARY KEY (VacancyID)
);