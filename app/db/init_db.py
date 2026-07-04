from decimal import Decimal
from sqlalchemy import text
from app.db.session import engine, SessionLocal
from app.db.models import Base, CompanyProfile

def init_db() -> None:
    """
    Ensures that:
    1. The company_profiles table has the 'id' serial primary key column.
    2. Other tables are created if missing (using Base.metadata.create_all).
    3. A default active company profile is seeded.
    """
    # 1. Non-destructively add id column to company_profiles if missing
    with engine.connect() as conn:
        # Check if company_profiles table exists
        table_exists = conn.execute(
            text("SELECT EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'company_profiles')")
        ).scalar()
        
        if table_exists:
            # Check if id column exists
            id_exists = conn.execute(
                text("SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_schema='public' AND table_name='company_profiles' AND column_name='id')")
            ).scalar()
            
            if not id_exists:
                print("Adding missing 'id' column to company_profiles table...")
                conn.execute(text("ALTER TABLE company_profiles ADD COLUMN id SERIAL PRIMARY KEY"))
                # Drop dummy column if it exists and is no longer needed
                dummy_exists = conn.execute(
                    text("SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_schema='public' AND table_name='company_profiles' AND column_name='dummy')")
                ).scalar()
                if dummy_exists:
                    conn.execute(text("ALTER TABLE company_profiles DROP COLUMN dummy"))
                conn.commit()

    # 2. Run standard create_all to create any missing tables
    Base.metadata.create_all(bind=engine)

    # 3. Seed active company profile if table is empty
    db = SessionLocal()
    try:
        profile_count = db.query(CompanyProfile).count()
        if profile_count == 0:
            print("Seeding default active company profile...")
            default_profile = CompanyProfile(
                profile_version="v1.0",
                company_name="GeM Bidder Corp",
                services=["Software Development", "IT Infrastructure", "Managed Services", "Email Apps", "Defender Licenses"],
                industries=["IT", "e-Governance", "Cloud", "Technology"],
                min_project_value_inr=Decimal("10000.00"),
                max_project_value_inr=Decimal("100000000.00"),
                min_turnover_inr=Decimal("500000.00"),
                certifications=["ISO 9001", "ISO 27001"],
                excluded_keywords=["construction", "civil", "plumbing", "mechanical"],
                preferred_keywords=["software", "cloud", "ai", "email", "support", "managed", "defender", "microsoft"],
                geo_preferences=["India"],
                active=True
            )
            db.add(default_profile)
            db.commit()
            print("Seeding completed successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding company profile: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
