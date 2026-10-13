from core.base import TIME_FORMAT, Report

HEADERS = ("login", "time_in", "time_out")


class SessionReport(Report):
    def __init__(self, path: str, sessions=()):
        super().__init__(path)
        self._sessions = list(sessions)

    @property
    def sessions(self) -> tuple:
        return tuple(self._sessions)

    def add(self, session):
        if session not in self._sessions:
            self._sessions.append(session)

    @staticmethod
    def _row(session) -> tuple:
        finish = session.time_out.strftime(TIME_FORMAT) if session.time_out else "-"
        return (session.login, session.time_in.strftime(TIME_FORMAT), finish)

    @staticmethod
    def _widths(rows) -> tuple:
        return tuple(
            max(len(str(row[index])) for row in rows) + 2 for index in range(len(HEADERS))
        )

    @staticmethod
    def _line(cells, widths, filler: str = " ") -> str:
        body = "|".join(str(cell).center(width, filler) for cell, width in zip(cells, widths))
        return f"|{body}|"

    def render(self) -> str:
        rows = [HEADERS] + [self._row(session) for session in sorted(self._sessions)]
        widths = self._widths(rows)
        border = "+" + "-" * (sum(widths) + len(widths) - 1) + "+"
        separator = self._line(("",) * len(HEADERS), widths, "-")
        lines = [border, self._line(rows[0], widths), separator]
        lines.extend(self._line(row, widths) for row in rows[1:])
        lines.append(border)
        return "\n".join(lines) + "\n"

    def __len__(self) -> int:
        return len(self._sessions)

    def __iter__(self):
        return iter(self._sessions)

    def __repr__(self) -> str:
        return f"SessionReport(path={self.path!r}, sessions={len(self._sessions)})"

    def __str__(self) -> str:
        return self.render()
