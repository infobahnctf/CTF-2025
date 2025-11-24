program BookManager;

uses
  SysUtils;

type
  TBook = record
    Title: AnsiString;
    Author: AnsiString;
  end;

  TCallback = procedure;

  PBookManager = ^TBookManager;
  TBookManager = record
    Books: array of TBook;
    BookCount: Integer;
    SecretCallback: TCallback;
  end;

var
  Manager: PBookManager;

procedure SecretBook;
begin
  Writeln('[Infobahn secret book] Shhh... this isn’t the secret book you’re looking for. Try flipping a few more bytes 📚💥');
  Flush(Output);
end;

procedure GetFlag;
var
  f: Integer;
  buf: array[0..255] of Byte;
  bytesRead: Integer;
begin
  f := FileOpen('flag.txt', fmOpenRead);
  if f = -1 then
  begin
    Writeln('Error: flag.txt not found.');
    Flush(Output);
    Exit;
  end;
  repeat
    bytesRead := FileRead(f, buf, SizeOf(buf));
    if bytesRead > 0 then
    begin
      Write(PAnsiChar(@buf[0]));
      Flush(Output);
    end;
  until bytesRead = 0;
  FileClose(f);
end;

procedure CreateBook;
var
  NewBook: TBook;
begin
  Write('Enter title: '); Flush(Output); ReadLn(NewBook.Title);
  Write('Enter author: '); Flush(Output); ReadLn(NewBook.Author);

  SetLength(Manager^.Books, Manager^.BookCount + 1);
  Manager^.Books[Manager^.BookCount] := NewBook;
  Inc(Manager^.BookCount);
  Writeln('Book added!'); Flush(Output);
end;

procedure ViewBooks;
var
  i: Integer;
begin
  if Manager^.BookCount = 0 then
  begin
    Writeln('No books available.'); Flush(Output);
    Exit;
  end;
  Writeln('Books in shelf:'); Flush(Output);
  for i := 0 to Manager^.BookCount - 1 do
  begin
    Writeln(i, ': "', Manager^.Books[i].Title, '" by ', Manager^.Books[i].Author);
    Flush(Output);
  end;
end;

procedure EditBook;
var
  Index: Integer;
  NewTitle, NewAuthor: string;
begin
  if Manager^.BookCount = 0 then
  begin
    Writeln('No books to edit.'); Flush(Output);
    Exit;
  end;

  Write('Enter book index to edit: '); Flush(Output); ReadLn(Index);
  Write('New title: '); Flush(Output); ReadLn(NewTitle);
  Write('New author: '); Flush(Output); ReadLn(NewAuthor);

  Move(NewTitle[1], Manager^.Books[Index].Title, Length(NewTitle));
  Move(NewAuthor[1], Manager^.Books[Index].Author, Length(NewAuthor));

  Writeln('Book updated.'); Flush(Output);
end;

procedure DeleteBook;
var
  Index, i: Integer;
begin
  if Manager^.BookCount = 0 then
  begin
    Writeln('No books to delete.'); Flush(Output);
    Exit;
  end;

  Write('Enter book index to delete: '); Flush(Output); ReadLn(Index);
  if (Index < 0) or (Index >= Manager^.BookCount) then
  begin
    Writeln('Invalid index.'); Flush(Output);
    Exit;
  end;

  for i := Index to Manager^.BookCount - 2 do
    Manager^.Books[i] := Manager^.Books[i + 1];
  SetLength(Manager^.Books, Manager^.BookCount - 1);
  Dec(Manager^.BookCount);
  Writeln('Book deleted.'); Flush(Output);
end;

procedure CallSecret;
begin
  if Assigned(Manager^.SecretCallback) then
  begin
    Manager^.SecretCallback;
    Flush(Output);
  end;
end;

procedure ShowMenu;
begin
  Writeln('=== Book Manager Menu ==='); Flush(Output);
  Writeln('1. Create book'); Flush(Output);
  Writeln('2. View books'); Flush(Output);
  Writeln('3. Edit book'); Flush(Output);
  Writeln('4. Delete book'); Flush(Output);
  Writeln('5. Get secret book'); Flush(Output);
  Writeln('6. Exit'); Flush(Output);
end;

var
  Choice: Integer;
begin
  New(Manager);
  Manager^.BookCount := 0;
  Manager^.SecretCallback := @SecretBook;

  repeat
    ShowMenu;
    Write('Choose an option: '); Flush(Output); ReadLn(Choice);
    case Choice of
      1: CreateBook;
      2: ViewBooks;
      3: EditBook;
      4: DeleteBook;
      5: CallSecret;
    end;
  until Choice = 6;

  Dispose(Manager);
  Writeln('Goodbye!'); Flush(Output);
end.
