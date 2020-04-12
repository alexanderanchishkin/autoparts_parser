from core.utilities import stopwatch


def main():
    TestMore().test(0)


class TestClass:
    @stopwatch.time(__qualname__)
    def test(self, a):
        for _ in range(1, 100000):
            a += 1


class TestMore(TestClass):
    pass


if __name__ == '__main__':
    main()
