# Category
class Category:

    def __init__(self, name, link) -> None:
        self.name = name
        self.link = link

    def __str__(self) -> str:
        return f'name = {self.name}, link = {self.link}'

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, o) -> bool:
        return self.name == o.name and self.link == o.link

    def __ne__(self, o: object) -> bool:
        return not self == o

    def __hash__(self) -> int:
        return hash(self.name)
