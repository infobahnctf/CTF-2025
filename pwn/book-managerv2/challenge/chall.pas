program BookManagerCTF;

uses
  SysUtils;

type
  TBook = packed record
    Title : array[0..31] of AnsiChar;
    Author: array[0..31] of AnsiChar;
  end;
  PBook = ^TBook;

var
  BookPtrs: array[0..255] of PBook;
  BookCount: Integer;

procedure CreateBook;
var
  TitleStr, AuthorStr: AnsiString;
  NewBook: PBook;
begin
  if BookCount >= Length(BookPtrs) then
  begin
    Writeln('Maximum number of books reached.');
    Exit;
  end;

  Write('Enter title: '); ReadLn(TitleStr);
  Write('Enter author: '); ReadLn(AuthorStr);

  GetMem(NewBook, SizeOf(TBook));
  FillChar(NewBook^, SizeOf(TBook), 0);

  Move(PAnsiChar(TitleStr)^, NewBook^.Title[0], Length(TitleStr));
  Move(PAnsiChar(AuthorStr)^, NewBook^.Author[0], Length(AuthorStr));

  BookPtrs[BookCount] := NewBook;
  Inc(BookCount);
  Writeln('Book added at index ', BookCount - 1);
end;

procedure ViewBooks;
var
  i: Integer;
begin
  if BookCount = 0 then
  begin
    Writeln('No books available.');
    Exit;
  end;
  Writeln('Books in shelf:');
  for i := 0 to BookCount - 1 do
    Writeln(i, ': "', PAnsiChar(@BookPtrs[i]^.Title[0]), '" by ', PAnsiChar(@BookPtrs[i]^.Author[0]));
end;

procedure EditBook;
var
  Index: Integer;
  NewTitle, NewAuthor: AnsiString;
begin
  if BookCount = 0 then
  begin
    Writeln('No books to edit.');
    Exit;
  end;

  ViewBooks;
  Write('Enter book index to edit: '); ReadLn(Index);
  if (Index < 0) or (Index >= BookCount) then
  begin
    Writeln('Invalid index.');
    Exit;
  end;

  Write('New title: '); ReadLn(NewTitle);
  Write('New author: '); ReadLn(NewAuthor);

  Move(NewTitle[1], BookPtrs[Index]^.Title[0], Length(NewTitle));
  Move(NewAuthor[1], BookPtrs[Index]^.Author[0], Length(NewAuthor));

  Writeln('Book updated.');
end;

procedure DeleteBook;
var
  Index, i: Integer;
begin
  if BookCount = 0 then
  begin
    Writeln('No books to delete.');
    Exit;
  end;

  ViewBooks;
  Write('Enter book index to delete: '); ReadLn(Index);
  if (Index < 0) or (Index >= BookCount) then
  begin
    Writeln('Invalid index.');
    Exit;
  end;

  FreeMem(BookPtrs[Index]);
  BookPtrs[Index] := nil;
  for i := Index to BookCount - 2 do
    BookPtrs[i] := BookPtrs[i + 1];
  Dec(BookCount);

  Writeln('Book deleted.');
end;

procedure ShowMenu;
begin
  Writeln('=== Book Manager Menu ===');
  Writeln('1. Create book');
  Writeln('2. View books');
  Writeln('3. Edit book');
  Writeln('4. Delete book');
  Writeln('0. Exit');
end;

var
  Choice: Integer;
begin
  BookCount := 0;

  repeat
    ShowMenu;
    Write('Choose an option: '); ReadLn(Choice);
    case Choice of
      1: CreateBook;
      2: ViewBooks;
      3: EditBook;
      4: DeleteBook;
    end;
  until Choice = 0;

  for Choice := 0 to BookCount - 1 do
    if BookPtrs[Choice] <> nil then
      FreeMem(BookPtrs[Choice]);

  Writeln('Goodbye!');
end.

