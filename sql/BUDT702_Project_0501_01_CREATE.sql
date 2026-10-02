USE BUDT702_Project_0501_01

-- Drop table queries
DROP TABLE IF EXISTS [Wsoc.Performance]
DROP TABLE IF EXISTS [Wsoc.Games]
DROP TABLE IF EXISTS [Wsoc.Season]
DROP TABLE IF EXISTS [Wsoc.Opponent]
DROP TABLE IF EXISTS [Wsoc.Player]

-- Create tables Opponent, Games, Player, and PlayedIn
CREATE TABLE [Wsoc.Player] (
		playerId CHAR(2) NOT NULL,
		playerFirstName VARCHAR(20),
		playerLastName VARCHAR (20) NOT NULL,
		playerNumber INTEGER, 
		CONSTRAINT pk_Player_playerId PRIMARY KEY (playerId) );

CREATE TABLE [Wsoc.Opponent] (
		opponentId CHAR(2) NOT NULL,
		opponentName VARCHAR(50) NOT NULL,
		CONSTRAINT pk_Opponent_opponentId PRIMARY KEY (opponentId) );

CREATE TABLE [Wsoc.Season] (
		seasonId CHAR(2) NOT NULL,
		seasonYear INTEGER,
		CONSTRAINT pk_Season_seasonId PRIMARY KEY (seasonId) );

CREATE TABLE [Wsoc.Games] (
		gameId CHAR(2) NOT NULL, 
		gameTerpScore INTEGER,
		gameOppScore INTEGER,
		gameDate DATE, 
		gameHome INTEGER, 
		opponentId CHAR(2) NOT NULL,
		seasonId CHAR(2) NOT NULL,
		CONSTRAINT pk_Games_gameId PRIMARY KEY (gameId),
		CONSTRAINT fk_Games_opponentId FOREIGN KEY (opponentId)
				REFERENCES [Wsoc.Opponent] (opponentId)
				ON DELETE NO ACTION ON UPDATE CASCADE,
		CONSTRAINT fk_Games_seasonId FOREIGN KEY (seasonId)
				REFERENCES [Wsoc.Season] (seasonId) 
				ON DELETE NO ACTION ON UPDATE NO ACTION );

CREATE TABLE [Wsoc.Performance] (
		playerId CHAR(2) NOT NULL,
		gameId CHAR(2) NOT NULL,
		performanceGoalsScore INTEGER,
		performanceAssists INTEGER,
		performanceShots INTEGER,
		performanceMinutesPlayed INTEGER,
		CONSTRAINT pk_Performance_playerId_gameId PRIMARY KEY (playerId, gameId),
		CONSTRAINT fk_Performance_playerId FOREIGN KEY (playerId)
				REFERENCES [Wsoc.Player] (playerId)
				ON DELETE NO ACTION ON UPDATE NO ACTION,
		CONSTRAINT fk_Performance_gameId FOREIGN KEY (gameId)
				REFERENCES [Wsoc.Games] (gameId)
				ON DELETE NO ACTION ON UPDATE NO ACTION );