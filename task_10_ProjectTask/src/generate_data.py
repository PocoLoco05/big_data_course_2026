import json
import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from faker import Faker


FINAL_STATUSES = {"решена", "закрыта"}
OPEN_STATUSES = {"новая", "в работе"}


def make_fake(seed: int = 42) -> Faker:
    fake = Faker("ru_RU")
    Faker.seed(seed)
    random.seed(seed)
    return fake


def generate_users(fake: Faker, n: int = 1000) -> pd.DataFrame:
    rows = []
    for user_id in range(1, n + 1):
        rows.append(
            {
                "user_id": user_id,
                "full_name": fake.name(),
                "email": fake.unique.email(),
                "phone": fake.phone_number(),
                "level": random.choices(["обычный", "премиум"], weights=[0.8, 0.2])[0],
            }
        )
    return pd.DataFrame(rows)


def generate_categories() -> pd.DataFrame:
    rows = [
        (1, "Проблемы со входом", "Ошибки авторизации, восстановление пароля, блокировка аккаунта"),
        (2, "Технический сбой", "Ошибки системы, недоступность сервиса, сбои в работе"),
        (3, "Оплата и подписка", "Проблемы со списанием средств, тарифами и подписками"),
        (4, "Функциональные вопросы", "Вопросы по использованию возможностей системы"),
        (5, "Жалобы и предложения", "Обратная связь, жалобы, улучшения сервиса"),
    ]
    return pd.DataFrame(rows, columns=["category_id", "name", "description"])


def generate_support_staff(fake: Faker, n: int = 10) -> pd.DataFrame:
    departments = ["Первая линия", "Технический отдел", "Финансовая поддержка", "Отдел качества", "VIP-поддержка"]
    rows = []
    for staff_id in range(1, n + 1):
        rows.append(
            {
                "staff_id": staff_id,
                "full_name": fake.name(),
                "department": random.choice(departments),
                "resolved_tickets_count": 0,
            }
        )
    return pd.DataFrame(rows)


def _comment_counts(n_tickets: int, total_comments: int, max_comments_per_ticket: int = 8) -> list[int]:
    if total_comments < n_tickets:
        raise ValueError("total_comments must be at least n_tickets")

    counts = [1] * n_tickets
    remaining = total_comments - n_tickets
    available = list(range(n_tickets))

    while remaining > 0:
        idx = random.choice(available)
        counts[idx] += 1
        remaining -= 1
        if counts[idx] >= max_comments_per_ticket:
            available.remove(idx)
        if not available and remaining > 0:
            available = list(range(n_tickets))

    return counts


def _date_between(start: datetime, end: datetime) -> datetime:
    if end <= start:
        return start
    seconds = int((end - start).total_seconds())
    return start + timedelta(seconds=random.randint(0, seconds))


def _ticket_priority(user_level: str) -> str:
    if user_level == "премиум":
        return random.choices(["низкий", "средний", "высокий", "критический"], weights=[0.1, 0.3, 0.4, 0.2])[0]
    return random.choices(["низкий", "средний", "высокий", "критический"], weights=[0.25, 0.45, 0.25, 0.05])[0]


def _generate_comments(
    fake: Faker,
    user_id: int,
    staff_id: int | None,
    created_at: datetime,
    updated_at: datetime,
    n_comments: int,
) -> str:
    comments = []
    for _ in range(n_comments):
        if staff_id is None:
            author_type = "user"
            author_id = user_id
        else:
            author_type = random.choices(["user", "staff"], weights=[0.55, 0.45])[0]
            author_id = user_id if author_type == "user" else staff_id

        comments.append(
            {
                "author_id": int(author_id),
                "author_type": author_type,
                "text": fake.sentence(nb_words=random.randint(6, 14)),
                "date": _date_between(created_at, updated_at).strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    comments.sort(key=lambda item: item["date"])
    return json.dumps(comments, ensure_ascii=False)


def generate_tickets(
    fake: Faker,
    users_df: pd.DataFrame,
    categories_df: pd.DataFrame,
    support_staff_df: pd.DataFrame,
    n: int = 5000,
    total_comments: int = 15000,
) -> pd.DataFrame:
    now = datetime.now().replace(microsecond=0)
    user_records = users_df[["user_id", "level"]].to_dict("records")
    category_ids = categories_df["category_id"].tolist()
    staff_ids = support_staff_df["staff_id"].tolist()
    comment_counts = _comment_counts(n, total_comments)

    rows = []
    for ticket_id in range(1, n + 1):
        user = random.choice(user_records)
        created_at = fake.date_time_between(start_date="-180d", end_date="now").replace(microsecond=0)
        status = random.choices(["новая", "в работе", "решена", "закрыта"], weights=[0.12, 0.24, 0.38, 0.26])[0]

        if status == "новая":
            staff_id = random.choice(staff_ids) if random.random() < 0.35 else None
            updated_at = _date_between(created_at, now)
            resolved_at = None
        elif status == "в работе":
            staff_id = random.choice(staff_ids)
            updated_at = _date_between(created_at + timedelta(hours=1), now)
            resolved_at = None
        else:
            staff_id = random.choice(staff_ids)
            max_resolved_at = min(created_at + timedelta(days=random.randint(1, 14), hours=random.randint(1, 23)), now)
            resolved_at = _date_between(created_at + timedelta(hours=1), max_resolved_at)
            updated_at = resolved_at

        comments_json = _generate_comments(
            fake=fake,
            user_id=int(user["user_id"]),
            staff_id=staff_id,
            created_at=created_at,
            updated_at=updated_at,
            n_comments=comment_counts[ticket_id - 1],
        )

        rows.append(
            {
                "ticket_id": ticket_id,
                "user_id": int(user["user_id"]),
                "category_id": int(random.choice(category_ids)),
                "subject": fake.sentence(nb_words=random.randint(4, 8)),
                "description": fake.text(max_nb_chars=240).replace("\n", " "),
                "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                "resolved_at": resolved_at.strftime("%Y-%m-%d %H:%M:%S") if resolved_at else "",
                "status": status,
                "priority": _ticket_priority(user["level"]),
                "staff_id": int(staff_id) if staff_id else "",
                "comments_json": comments_json,
            }
        )

    return pd.DataFrame(rows)


def refresh_staff_resolved_count(support_staff_df: pd.DataFrame, tickets_df: pd.DataFrame) -> pd.DataFrame:
    resolved_counts = (
        tickets_df[tickets_df["status"].isin(FINAL_STATUSES)]
        .groupby("staff_id")
        .size()
        .rename("resolved_tickets_count")
        .reset_index()
    )

    result = support_staff_df.drop(columns=["resolved_tickets_count"]).merge(
        resolved_counts,
        on="staff_id",
        how="left",
    )
    result["resolved_tickets_count"] = result["resolved_tickets_count"].fillna(0).astype(int)
    return result


def generate_all(output_dir: Path, seed: int = 42) -> dict[str, pd.DataFrame]:
    output_dir.mkdir(parents=True, exist_ok=True)
    fake = make_fake(seed)

    users_df = generate_users(fake)
    categories_df = generate_categories()
    support_staff_df = generate_support_staff(fake)
    tickets_df = generate_tickets(fake, users_df, categories_df, support_staff_df)
    support_staff_df = refresh_staff_resolved_count(support_staff_df, tickets_df)

    frames = {
        "users": users_df,
        "categories": categories_df,
        "support_staff": support_staff_df,
        "tickets": tickets_df,
    }

    for name, frame in frames.items():
        frame.to_csv(output_dir / f"{name}.csv", index=False)

    return frames


if __name__ == "__main__":
    project_dir = Path(__file__).resolve().parents[1]
    generate_all(project_dir / "data" / "raw")
