# This is a test db for speed comparison
# Writes 500 records

CREATE TABLE if not exists "albums"
(
    [AlbumId] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    [Title] NVARCHAR(160)  NOT NULL,
    [ArtistId] INTEGER  NOT NULL,
    FOREIGN KEY ([ArtistId]) REFERENCES "artists" ([ArtistId])
                ON DELETE NO ACTION ON UPDATE NO ACTION
);

# No index for testing
#CREATE INDEX [IFK_AlbumArtistId] ON "albums" ([ArtistId]);

# Repeat operation 500 times

insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);
insert into albums (Title, ArtistId) values("Hello", 1);

# EOF