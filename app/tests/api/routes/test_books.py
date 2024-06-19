from random import randint

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.models.book import Book


def test_create_book(client: TestClient) -> None:
    data = {"id": str(randint(100000, 999999)), "title": "Test Book 1", "author": "Test Author 1"}
    response = client.post(
        f"{settings.API_V1_STR}/books/",
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == data["id"]
    assert content["title"] == data["title"]
    assert content["author"] == data["author"]
    assert content["on_loan"] is False
    assert content["loan_date"] is None
    assert content["loanee_id"] is None


def test_read_books(
    client: TestClient, db: Session
) -> None:

    book_1 = Book(id=str(randint(100000, 999999)), title="Test Book 2", author="Test Author 1",  on_loan=False)
    book_2 = Book(id=str(randint(100000, 999999)), title="Test Book 3", author="Test Author 1",  on_loan=False)
    db.add(book_1)
    db.add(book_2)
    db.commit()

    response = client.get(
        f"{settings.API_V1_STR}/books/"
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content) >= 2


def test_update_book(
    client: TestClient, db: Session
) -> None:
    book = db.get(Book, "123457")
    if not book:
        book = Book(id="123457", title="Test Book 2", author="Test Author 1",  on_loan=False)
        db.add(book)
        db.commit()
    data = {"on_loan": True, "loanee_id": "123456"}
    response = client.patch(
        f"{settings.API_V1_STR}/books/{book.id}",
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["on_loan"] is True
    assert content["loanee_id"] == data["loanee_id"]


def test_update_item_not_found(
    client: TestClient
) -> None:
    data = {"on_loan": True, "loanee_id": "123456"}
    response = client.patch(
        f"{settings.API_V1_STR}/books/999",
        json=data,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Book not found"


def test_delete_item(
    client: TestClient, db: Session
) -> None:
    book = db.get(Book, "123457")
    if not book:
        book = Book(id="123457", title="Test Book 2", author="Test Author 1",  on_loan=False)
        db.add(book)
        db.commit()
    response = client.delete(
        f"{settings.API_V1_STR}/books/{book.id}",
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "Book deleted successfully"


def test_delete_item_not_found(
    client: TestClient
) -> None:
    response = client.delete(
        f"{settings.API_V1_STR}/books/999",
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Book not found"
