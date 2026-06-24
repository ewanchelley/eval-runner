
from pydantic import BaseModel

class TestCase(BaseModel):
    id: str
    prompt: str
    check: str
    expected: str

def main():
    pass


if __name__ == "__main__":
    main()
