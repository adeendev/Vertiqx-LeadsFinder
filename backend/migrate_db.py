import sqlite3
from models import Project, Lead
from database import engine
from sqlmodel import Session, select

DB_PATH = "leads.db"

def migrate():
    print("Migrating database...")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check columns in lead table
        cursor.execute("PRAGMA table_info(lead)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if "project_name" not in columns:
            print("Adding project_name column...")
            cursor.execute("ALTER TABLE lead ADD COLUMN project_name VARCHAR DEFAULT 'Default Project'")
            
        if "facebook" not in columns:
            print("Adding facebook column...")
            cursor.execute("ALTER TABLE lead ADD COLUMN facebook VARCHAR")

        if "instagram" not in columns:
            print("Adding instagram column...")
            cursor.execute("ALTER TABLE lead ADD COLUMN instagram VARCHAR")

        if "linkedin" not in columns:
            print("Adding linkedin column...")
            cursor.execute("ALTER TABLE lead ADD COLUMN linkedin VARCHAR")
            
        if "pain_points" not in columns:
            print("Adding pain_points column...")
            cursor.execute("ALTER TABLE lead ADD COLUMN pain_points VARCHAR")

        if "email_sent" not in columns:
            print("Adding email_sent column...")
            cursor.execute("ALTER TABLE lead ADD COLUMN email_sent BOOLEAN DEFAULT 0")

        if "email_sent_at" not in columns:
            print("Adding email_sent_at column...")
            cursor.execute("ALTER TABLE lead ADD COLUMN email_sent_at DATETIME")

        if "email_status" not in columns:
            print("Adding email_status column...")
            cursor.execute("ALTER TABLE lead ADD COLUMN email_status VARCHAR")
            
        # Create Project table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR NOT NULL UNIQUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        
        # Backfill projects
        print("Backfilling projects...")
        with Session(engine) as session:
            # Get distinct project names from leads
            lead_projects = session.exec(select(Lead.project_name).distinct()).all()
            
            for proj_name in lead_projects:
                if not proj_name: continue
                
                # Check if exists in Project table
                existing = session.exec(select(Project).where(Project.name == proj_name)).first()
                if not existing:
                    print(f"Creating project record for: {proj_name}")
                    session.add(Project(name=proj_name))
            
            session.commit()

        print("Migration complete.")
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
