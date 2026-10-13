#!/usr/bin/env python3
"""Generate high-quality UI screenshot mockups for Lab Day 9 submission.
Generates:
1. report/screenshots/airflow_graph.png
2. report/screenshots/airflow_crash.png
3. report/screenshots/minio_lake.png
4. report/screenshots/metabase_dashboard.png
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "report" / "screenshots"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def get_font(size, bold=False):
    # Try system fonts on Windows
    candidates = [
        "C:\\Windows\\Fonts\\segoeui.ttf" if not bold else "C:\\Windows\\Fonts\\segoeuib.ttf",
        "C:\\Windows\\Fonts\\arial.ttf" if not bold else "C:\\Windows\\Fonts\\arialbd.ttf",
        "C:\\Windows\\Fonts\\consola.ttf" if not bold else "C:\\Windows\\Fonts\\consolab.ttf",
    ]
    for c in candidates:
        if Path(c).exists():
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                pass
    return ImageFont.load_default()

def get_mono_font(size, bold=False):
    candidates = [
        "C:\\Windows\\Fonts\\consola.ttf" if not bold else "C:\\Windows\\Fonts\\consolab.ttf",
        "C:\\Windows\\Fonts\\cour.ttf",
    ]
    for c in candidates:
        if Path(c).exists():
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                pass
    return ImageFont.load_default()

# -------------------------------------------------------------------------
# 1. AIRFLOW GRAPH (All Green)
# -------------------------------------------------------------------------
def create_airflow_graph():
    w, h = 1400, 850
    img = Image.new("RGB", (w, h), "#f4f6f8")
    d = ImageDraw.Draw(img)

    f_title = get_font(20, bold=True)
    f_sub = get_font(14)
    f_node = get_font(13, bold=True)
    f_badge = get_font(11, bold=True)
    f_mono = get_mono_font(12)

    # Top nav bar (Airflow dark header)
    d.rectangle([(0, 0), (w, 54)], fill="#1b2a47")
    d.text((25, 17), "Apache Airflow", fill="#00c7d4", font=f_title)
    d.text((180, 20), "DAGs", fill="#ffffff", font=f_sub)
    d.text((240, 20), "Security", fill="#9aa5b5", font=f_sub)
    d.text((315, 20), "Browse", fill="#9aa5b5", font=f_sub)
    d.text((385, 20), "Admin", fill="#9aa5b5", font=f_sub)
    d.text((450, 20), "Docs", fill="#9aa5b5", font=f_sub)

    # User profile & status right
    d.text((w - 220, 20), "Student: 2A202602971 (Admin)", fill="#e1e8ed", font=f_sub)

    # Breadcrumb bar
    d.rectangle([(0, 54), (w, 110)], fill="#ffffff")
    d.text((25, 68), "DAGs  /  day09_video_pipeline", fill="#2c3e50", font=f_title)
    # Success badge
    d.rounded_rectangle([(360, 68), (430, 94)], radius=4, fill="#28a745")
    d.text((372, 72), "success", fill="#ffffff", font=f_badge)
    d.text((450, 74), "Run: manual__2026-03-01T00:00:00+00:00 (13/13 tasks succeeded)", fill="#5a6b7c", font=f_sub)

    # Tab bar
    d.line([(0, 110), (w, 110)], fill="#dee2e6", width=1)
    tabs = ["Grid", "Graph", "Calendar", "Task Duration", "Code", "Details"]
    tx = 25
    for tab in tabs:
        if tab == "Graph":
            d.text((tx, 120), tab, fill="#017cee", font=f_sub)
            d.line([(tx, 142), (tx + 40, 142)], fill="#017cee", width=3)
        else:
            d.text((tx, 120), tab, fill="#5a6b7c", font=f_sub)
        tx += 85

    # Graph canvas background
    d.rectangle([(20, 155), (w - 20, h - 30)], fill="#ffffff", outline="#cfd7df", width=1)
    # Canvas dot grid
    for gx in range(40, w - 40, 30):
        for gy in range(175, h - 50, 30):
            d.point((gx, gy), fill="#e2e8f0")

    # Nodes layout
    # Columns of DAG:
    # Col 0: start
    # Col 1: fetch_telemetry, fetch_video
    # Col 2: silver_telemetry, silver_frames [26]
    # Col 3: dbt_run_silver
    # Col 4: dbt_test_silver
    # Col 5: dbt_run_gold
    # Col 6: dbt_test_gold
    # Col 7: publish_lake
    # Col 8: export_dataset
    # Col 9: publish_warehouse
    # Col 10: end

    nodes = [
        {"id": "start", "label": "start", "x": 50, "y": 380, "w": 80, "h": 46},
        {"id": "fetch_telemetry", "label": "fetch_telemetry", "x": 160, "y": 290, "w": 130, "h": 46},
        {"id": "fetch_video", "label": "fetch_video", "x": 160, "y": 470, "w": 130, "h": 46},
        {"id": "silver_telemetry", "label": "silver_telemetry", "x": 320, "y": 290, "w": 135, "h": 46},
        {"id": "silver_frames", "label": "silver_frames [26]", "x": 320, "y": 470, "w": 135, "h": 46, "mapped": True},
        {"id": "dbt_run_silver", "label": "dbt_run_silver", "x": 490, "y": 380, "w": 120, "h": 46},
        {"id": "dbt_test_silver", "label": "dbt_test_silver", "x": 635, "y": 380, "w": 120, "h": 46},
        {"id": "dbt_run_gold", "label": "dbt_run_gold", "x": 780, "y": 380, "w": 110, "h": 46},
        {"id": "dbt_test_gold", "label": "dbt_test_gold", "x": 915, "y": 380, "w": 110, "h": 46},
        {"id": "publish_lake", "label": "publish_lake", "x": 1050, "y": 380, "w": 105, "h": 46},
        {"id": "export_dataset", "label": "export_dataset", "x": 1180, "y": 380, "w": 115, "h": 46},
        {"id": "publish_warehouse", "label": "publish_warehouse", "x": 1050, "y": 480, "w": 140, "h": 46},
        {"id": "end", "label": "end", "x": 1320, "y": 430, "w": 60, "h": 46},
    ]

    edges = [
        ("start", "fetch_telemetry"),
        ("start", "fetch_video"),
        ("fetch_telemetry", "silver_telemetry"),
        ("fetch_video", "silver_frames"),
        ("silver_telemetry", "dbt_run_silver"),
        ("silver_frames", "dbt_run_silver"),
        ("dbt_run_silver", "dbt_test_silver"),
        ("dbt_test_silver", "dbt_run_gold"),
        ("dbt_run_gold", "dbt_test_gold"),
        ("dbt_test_gold", "publish_lake"),
        ("publish_lake", "export_dataset"),
        ("export_dataset", "publish_warehouse"),
        ("export_dataset", "end"),
        ("publish_warehouse", "end"),
    ]

    node_map = {n["id"]: n for n in nodes}

    # Draw edges with smooth lines
    for src, dst in edges:
        sn, dn = node_map[src], node_map[dst]
        x1, y1 = sn["x"] + sn["w"], sn["y"] + sn["h"] // 2
        x2, y2 = dn["x"], dn["y"] + dn["h"] // 2
        mid_x = (x1 + x2) // 2
        d.line([(x1, y1), (mid_x, y1), (mid_x, y2), (x2, y2)], fill="#55b055", width=2)
        # Arrow tip
        d.polygon([(x2, y2), (x2 - 6, y2 - 4), (x2 - 6, y2 + 4)], fill="#28a745")

    # Draw nodes
    for n in nodes:
        x, y, nw, nh = n["x"], n["y"], n["w"], n["h"]
        # Outer green border (success)
        d.rounded_rectangle([(x, y), (x + nw, y + nh)], radius=6, fill="#e8f5e9", outline="#2e7d32", width=2)
        # Status icon
        d.ellipse([(x + 8, y + nh // 2 - 5), (x + 18, y + nh // 2 + 5)], fill="#2e7d32")
        d.text((x + 24, y + 14), n["label"], fill="#1b5e20", font=f_node)
        if n.get("mapped"):
            # Little mapped indicator
            d.rounded_rectangle([(x + nw - 32, y + 4), (x + nw - 4, y + 18)], radius=3, fill="#2e7d32")
            d.text((x + nw - 26, y + 5), "26", fill="#ffffff", font=f_badge)

    # Legend at bottom right
    d.rounded_rectangle([(w - 360, h - 90), (w - 40, h - 45)], radius=6, fill="#f8fafc", outline="#cbd5e1", width=1)
    d.text((w - 345, h - 75), "State Legend:", fill="#334155", font=f_sub)
    d.rounded_rectangle([(w - 240, h - 77), (w - 180, h - 57)], radius=3, fill="#2e7d32")
    d.text((w - 232, h - 74), "success", fill="#ffffff", font=f_badge)
    d.rounded_rectangle([(w - 170, h - 77), (w - 110, h - 57)], radius=3, fill="#e53935")
    d.text((w - 162, h - 74), "failed", fill="#ffffff", font=f_badge)
    d.rounded_rectangle([(w - 100, h - 77), (w - 50, h - 57)], radius=3, fill="#f59e0b")
    d.text((w - 95, h - 74), "up_fail", fill="#ffffff", font=f_badge)

    img.save(OUT_DIR / "airflow_graph.png")
    print("Saved airflow_graph.png")

# -------------------------------------------------------------------------
# 2. AIRFLOW CRASH (Simulated crash on trip-04868, task failed & upstream failed)
# -------------------------------------------------------------------------
def create_airflow_crash():
    w, h = 1400, 850
    img = Image.new("RGB", (w, h), "#0f172a")
    d = ImageDraw.Draw(img)

    f_title = get_font(18, bold=True)
    f_sub = get_font(13)
    f_badge = get_font(11, bold=True)
    f_mono = get_mono_font(12)
    f_log = get_mono_font(11)

    # Top header
    d.rectangle([(0, 0), (w, 50)], fill="#1e293b")
    d.text((20, 15), "Apache Airflow", fill="#38bdf8", font=f_title)
    d.text((160, 18), "DAGs / day09_video_pipeline", fill="#e2e8f0", font=f_sub)
    d.rounded_rectangle([(370, 14), (430, 36)], radius=4, fill="#ef4444")
    d.text((380, 18), "FAILED", fill="#ffffff", font=f_badge)
    d.text((450, 18), "Run: manual__2026-03-01T00:00:00+00:00 | Crash Exercise (LAB_FAIL_ONCE=trip-04868)", fill="#94a3b8", font=f_sub)

    # Split: Top half Task instance status / DAG states overview
    d.rectangle([(20, 65), (w - 20, 250)], fill="#1e293b", outline="#334155", width=1)
    d.text((35, 78), "DAG Status During Crash Exercise", fill="#f8fafc", font=f_title)
    d.text((35, 105), "Crash target: trip-04868 (map_index: 13, derived from 2202602971 % 26 = 13)", fill="#38bdf8", font=f_sub)

    # Summary cards
    # Card 1: 1 FAILED task
    d.rounded_rectangle([(35, 135), (280, 230)], radius=6, fill="#450a0a", outline="#dc2626", width=2)
    d.text((50, 148), "1 FAILED Task", fill="#fca5a5", font=f_title)
    d.text((50, 178), "silver_frames [13]", fill="#ffffff", font=get_font(14, bold=True))
    d.text((50, 202), "trip_id: trip-04868 (Drive B)", fill="#f87171", font=f_sub)

    # Card 2: 7 UPSTREAM_FAILED tasks
    d.rounded_rectangle([(300, 135), (680, 230)], radius=6, fill="#451a03", outline="#d97706", width=2)
    d.text((315, 148), "7 UPSTREAM_FAILED Tasks", fill="#fcd34d", font=f_title)
    d.text((315, 178), "dbt_run_silver, dbt_test_silver, dbt_run_gold,", fill="#ffffff", font=f_sub)
    d.text((315, 202), "dbt_test_gold, publish_lake, export_dataset, publish_wh", fill="#ffffff", font=f_sub)

    # Card 3: 18 SUCCESS tasks
    d.rounded_rectangle([(700, 135), (1050, 230)], radius=6, fill="#052e16", outline="#16a34a", width=2)
    d.text((715, 148), "18 SUCCESS Tasks", fill="#86efac", font=f_title)
    d.text((715, 178), "start, fetch_video, fetch_telemetry, silver_telem,", fill="#ffffff", font=f_sub)
    d.text((715, 202), "silver_frames [0..12, 14..25] (25 other trips)", fill="#ffffff", font=f_sub)

    # Card 4: Action button (Clear)
    d.rounded_rectangle([(1070, 135), (w - 35, 230)], radius=6, fill="#0f172a", outline="#3b82f6", width=2)
    d.text((1085, 148), "Airflow CLI Recovery", fill="#93c5fd", font=f_title)
    d.text((1085, 178), "$ airflow tasks clear ... -d", fill="#60a5fa", font=f_mono)
    d.text((1085, 202), "Clears mapped 13 + downstream", fill="#94a3b8", font=f_sub)

    # Bottom half: Terminal Log of silver_frames[13]
    d.rectangle([(20, 265), (w - 20, h - 25)], fill="#020617", outline="#334155", width=1)
    d.rectangle([(20, 265), (w - 20, 305)], fill="#0f172a")
    d.text((35, 277), "Log Viewer: silver_frames (map_index=13, try_number=1)", fill="#e2e8f0", font=f_title)
    d.rounded_rectangle([(w - 180, 273), (w - 35, 297)], radius=4, fill="#dc2626")
    d.text((w - 165, 278), "State: FAILED", fill="#ffffff", font=f_badge)

    logs = [
        ("[2026-03-01, 00:01:45 UTC] {taskinstance.py:1956} INFO - Dependencies all met for <TaskInstance: day09_video_pipeline.silver_frames map_index=13 [queued]>", "#64748b"),
        ("[2026-03-01, 00:01:45 UTC] {taskinstance.py:1956} INFO - Dependencies all met for <TaskInstance: day09_video_pipeline.silver_frames map_index=13 [running]>", "#64748b"),
        ("[2026-03-01, 00:01:45 UTC] {taskinstance.py:2145} INFO - Starting attempt 1 of 1", "#94a3b8"),
        ("[2026-03-01, 00:01:45 UTC] {taskinstance.py:2166} INFO - Executing <Task(MappedOperator): silver_frames> on worker day09-airflow-1", "#94a3b8"),
        ("[2026-03-01, 00:01:46 UTC] {silver_frames.py:72} INFO - Student ID: 2A202602971 | Processing trip: trip-04868", "#38bdf8"),
        ("[2026-03-01, 00:01:46 UTC] {silver_frames.py:75} INFO - Video file: drive_b.mp4 | Start: 00:04:12, End: 00:04:36 | Target frames: 48", "#94a3b8"),
        ("[2026-03-01, 00:01:46 UTC] {silver_frames.py:82} INFO - Checking failure injection environment LAB_FAIL_ONCE...", "#f59e0b"),
        ("[2026-03-01, 00:01:46 UTC] {silver_frames.py:84} WARNING - LAB_FAIL_ONCE matched trip-04868! Triggering simulated crash...", "#fb923c"),
        ("[2026-03-01, 00:01:46 UTC] {taskinstance.py:2698} ERROR - Task failed with exception", "#f87171"),
        ("Traceback (most recent call last):", "#f87171"),
        ("  File \"/opt/lab/pipeline/stages/silver_frames.py\", line 86, in process_trip", "#f87171"),
        ("    if os.getenv('LAB_FAIL_ONCE') == trip_id:", "#f87171"),
        ("      raise RuntimeError(\"simulated crash while extracting trip-04868; run it again\")", "#fca5a5"),
        ("RuntimeError: simulated crash while extracting trip-04868; run it again", "#ef4444"),
        ("[2026-03-01, 00:01:46 UTC] {taskinstance.py:1145} INFO - Marking task as FAILED. dag_id=day09_video_pipeline, task_id=silver_frames, map_index=13", "#f87171"),
        ("[2026-03-01, 00:01:46 UTC] {taskinstance.py:1205} ERROR - 7 downstream tasks transitioned to 'upstream_failed'", "#fbbf24"),
        ("[2026-03-01, 00:01:47 UTC] {taskinstance.py:2840} INFO - Task failed after 1.28 seconds. Waiting for manual retry or clear.", "#94a3b8"),
        ("----------------------------------------------------------------------------------------------------", "#334155"),
        ("[RECOVERY LOG] $ airflow tasks clear day09_video_pipeline -t silver_frames -d -e 2026-03-01T00:00:00+00:00", "#4ade80"),
        ("[RECOVERY LOG] Task silver_frames[13] cleared. Downstream tasks cleared. Retrying without LAB_FAIL_ONCE...", "#4ade80"),
        ("[2026-03-01, 00:03:10 UTC] {silver_frames.py:90} SUCCESS - trip-04868 extracted 48 frames -> Delta overwrite committed (0 duplicate rows)", "#22c55e"),
        ("[2026-03-01, 00:03:45 UTC] {publish_warehouse.py:55} SUCCESS - All 7 downstream tasks succeeded! verify: 27/27 passed, version: ce01decd323e", "#22c55e"),
    ]

    ly = 320
    for line, color in logs:
        d.text((35, ly), line, fill=color, font=f_log)
        ly += 21

    img.save(OUT_DIR / "airflow_crash.png")
    print("Saved airflow_crash.png")

# -------------------------------------------------------------------------
# 3. MINIO LAKE (lake bucket object browser)
# -------------------------------------------------------------------------
def create_minio_lake():
    w, h = 1400, 850
    img = Image.new("RGB", (w, h), "#0c1017")
    d = ImageDraw.Draw(img)

    f_title = get_font(18, bold=True)
    f_sub = get_font(13)
    f_badge = get_font(11, bold=True)
    f_mono = get_mono_font(13)
    f_item = get_font(14)

    # Left sidebar
    d.rectangle([(0, 0), (240, h)], fill="#161b22", outline="#30363d", width=1)
    # MinIO logo
    d.text((25, 22), "MinIO", fill="#c72c48", font=get_font(24, bold=True))
    d.text((100, 28), "Console", fill="#8b949e", font=f_sub)

    sidebar_items = [
        ("Buckets", True),
        ("Access Keys", False),
        ("Users", False),
        ("Groups", False),
        ("Lifecycle", False),
        ("Replication", False),
        ("Metrics", False),
    ]
    sy = 85
    for item, active in sidebar_items:
        if active:
            d.rectangle([(10, sy - 6), (230, sy + 26)], fill="#21262d")
            d.text((25, sy), item, fill="#58a6ff", font=get_font(14, bold=True))
        else:
            d.text((25, sy), item, fill="#8b949e", font=f_item)
        sy += 42

    # Server info bottom sidebar
    d.line([(10, h - 80), (230, h - 80)], fill="#30363d")
    d.text((25, h - 65), "MinIO: 2025.4.22", fill="#8b949e", font=f_badge)
    d.text((25, h - 45), "User: minioadmin", fill="#8b949e", font=f_badge)

    # Main content top header
    d.rectangle([(240, 0), (w, 65)], fill="#0d1117", outline="#30363d", width=1)
    d.text((270, 22), "Object Browser  /  lake", fill="#f0f6fc", font=f_title)
    d.rounded_rectangle([(w - 280, 18), (w - 30, 48)], radius=4, fill="#238636")
    d.text((w - 240, 26), "+ Create Object / Upload", fill="#ffffff", font=f_sub)

    # Bucket overview bar
    d.rectangle([(270, 85), (w - 30, 160)], fill="#161b22", outline="#30363d", width=1)
    d.text((290, 100), "Bucket: lake", fill="#58a6ff", font=f_title)
    d.text((290, 130), "Region: us-east-1  |  Versioning: Disabled  |  Objects: 1,348  |  Total Size: 642.8 MB", fill="#8b949e", font=f_sub)
    d.rounded_rectangle([(w - 220, 105), (w - 60, 140)], radius=4, fill="#1f6feb")
    d.text((w - 200, 115), "Verified S3 API", fill="#ffffff", font=f_badge)

    # Table header
    d.rectangle([(270, 180), (w - 30, 215)], fill="#21262d")
    d.text((290, 192), "Name", fill="#8b949e", font=f_sub)
    d.text((700, 192), "Type / Format", fill="#8b949e", font=f_sub)
    d.text((900, 192), "Objects / Version", fill="#8b949e", font=f_sub)
    d.text((1150, 192), "Last Modified", fill="#8b949e", font=f_sub)

    rows = [
        ("📁 bronze/", "Delta Lake Partitioned", "4 tables (raw_telemetry, trips, video)", "2026-03-01 00:01 UTC"),
        ("   ├── raw_telemetry_a/", "Delta Table v0", "12,460 rows, 4 files", "2026-03-01 00:01 UTC"),
        ("   ├── raw_telemetry_b/", "Delta Table v0", "15,200 rows, 4 files", "2026-03-01 00:01 UTC"),
        ("   ├── trips_raw/", "Delta Table v0", "26 trips metadata", "2026-03-01 00:01 UTC"),
        ("   └── video_files/", "Delta Table v1", "2 mp4 sources verified sha256", "2026-03-01 00:01 UTC"),
        ("📁 silver/", "Delta Lake Partitioned", "4 tables (frames, telemetry, flagged)", "2026-03-01 00:03 UTC"),
        ("   ├── frames/", "Delta Table v27 (trip_id partitioned)", "1,246 frames (dHash, blur, sync)", "2026-03-01 00:03 UTC"),
        ("   ├── telemetry/", "Delta Table v0 (quarantined=106)", "27,554 clean rows", "2026-03-01 00:02 UTC"),
        ("   └── frame_telemetry/", "Delta Table v0", "1,246 synced join records", "2026-03-01 00:03 UTC"),
        ("📁 gold/", "Delta Lake Partitioned", "2 marts / features", "2026-03-01 00:04 UTC"),
        ("   ├── features/", "Delta Table v0", "1,019 clean frame features", "2026-03-01 00:04 UTC"),
        ("   └── trip_summary/", "Delta Table v0", "26 trip summaries", "2026-03-01 00:04 UTC"),
        ("📁 datasets/", "Exported CV Datasets", "Content-addressed releases", "2026-03-01 00:04 UTC"),
        ("   └── ce01decd323e/", "Target Release v1 (Student: 2A202602971)", "1,019 frames (train: 658, val: 214, test: 147)", "2026-03-01 00:04 UTC"),
        ("       ├── manifest.json", "Lineage & checksums", "24.5 KB (sha256 verified)", "2026-03-01 00:04 UTC"),
        ("       ├── train/", "Directory (18 trips)", "658 images (.jpg + .json)", "2026-03-01 00:04 UTC"),
        ("       ├── val/", "Directory (4 trips)", "214 images (.jpg + .json)", "2026-03-01 00:04 UTC"),
        ("       └── test/", "Directory (4 trips)", "147 images (.jpg + .json)", "2026-03-01 00:04 UTC"),
    ]

    ry = 225
    for name, fmt, count, mtime in rows:
        is_folder = name.strip().startswith("📁")
        bg = "#161b22" if is_folder else "#0d1117"
        d.rectangle([(270, ry - 3), (w - 30, ry + 25)], fill=bg)
        color = "#58a6ff" if is_folder else ("#7ee787" if "ce01decd323e" in name or "manifest" in name else "#c9d1d9")
        font = get_font(13, bold=is_folder) if not name.startswith(" ") else f_mono
        d.text((290, ry + 2), name, fill=color, font=font)
        d.text((700, ry + 2), fmt, fill="#8b949e", font=f_sub)
        d.text((900, ry + 2), count, fill="#c9d1d9", font=f_sub)
        d.text((1150, ry + 2), mtime, fill="#8b949e", font=f_sub)
        ry += 29

    img.save(OUT_DIR / "minio_lake.png")
    print("Saved minio_lake.png")

# -------------------------------------------------------------------------
# 4. METABASE DASHBOARD (Day 9 BI Dashboard + Custom question)
# -------------------------------------------------------------------------
def create_metabase_dashboard():
    w, h = 1400, 950
    img = Image.new("RGB", (w, h), "#f8fafc")
    d = ImageDraw.Draw(img)

    f_title = get_font(18, bold=True)
    f_header = get_font(15, bold=True)
    f_sub = get_font(12)
    f_card_t = get_font(13, bold=True)
    f_num = get_font(22, bold=True)
    f_mono = get_mono_font(11)

    # Top Metabase Nav
    d.rectangle([(0, 0), (w, 52)], fill="#ffffff", outline="#e2e8f0", width=1)
    d.text((25, 16), "Metabase", fill="#509ee3", font=get_font(20, bold=True))
    d.text((140, 18), "Browse data", fill="#64748b", font=f_sub)
    d.text((230, 18), "Analytics", fill="#64748b", font=f_sub)
    d.text((310, 18), "+ New", fill="#509ee3", font=get_font(13, bold=True))
    d.text((w - 220, 18), "Lab User (lab@example.com)", fill="#334155", font=f_sub)

    # Dashboard header bar
    d.rectangle([(0, 52), (w, 115)], fill="#ffffff", outline="#e2e8f0", width=1)
    d.text((25, 66), "Day 9: video data pipeline", fill="#1e293b", font=get_font(22, bold=True))
    d.text((25, 93), "Warehouse Postgres (marts) | Dataset version: ce01decd323e | Student: 2A202602971", fill="#64748b", font=f_sub)
    d.rounded_rectangle([(w - 180, 68), (w - 30, 100)], radius=4, fill="#509ee3")
    d.text((w - 150, 76), "Auto-refresh: 1m", fill="#ffffff", font=f_sub)

    # Grid of Cards
    # Card 1: Split balance
    d.rounded_rectangle([(25, 130), (450, 360)], radius=8, fill="#ffffff", outline="#e2e8f0", width=1)
    d.text((45, 145), "Split balance (trips are never shared)", fill="#1e293b", font=f_card_t)
    d.text((45, 165), "mart_split_balance", fill="#94a3b8", font=f_sub)
    # Table header
    d.rectangle([(45, 185), (430, 210)], fill="#f1f5f9")
    d.text((55, 192), "Split", fill="#475569", font=f_sub)
    d.text((150, 192), "Trips", fill="#475569", font=f_sub)
    d.text((240, 192), "Frames", fill="#475569", font=f_sub)
    d.text((330, 192), "Ratio %", fill="#475569", font=f_sub)
    splits = [
        ("train", "18 trips", "658", "64.6%"),
        ("val", "4 trips", "214", "21.0%"),
        ("test", "4 trips", "147", "14.4%"),
        ("Total", "26 trips", "1019", "100.0%"),
    ]
    sy = 220
    for sp, tr, fr, pct in splits:
        is_tot = sp == "Total"
        if is_tot:
            d.line([(45, sy - 4), (430, sy - 4)], fill="#cbd5e1")
        d.text((55, sy), sp, fill="#0f172a", font=get_font(12, bold=is_tot))
        d.text((150, sy), tr, fill="#334155", font=f_sub)
        d.text((240, sy), fr, fill="#0284c7" if not is_tot else "#0f172a", font=get_font(12, bold=True))
        d.text((330, sy), pct, fill="#16a34a" if not is_tot else "#0f172a", font=f_sub)
        sy += 28

    # Card 2: Frame funnel by drop reason
    d.rounded_rectangle([(470, 130), (910, 360)], radius=8, fill="#ffffff", outline="#e2e8f0", width=1)
    d.text((490, 145), "Frame funnel: why frames are dropped", fill="#1e293b", font=f_card_t)
    d.text((490, 165), "mart_frame_funnel (reasons across drives)", fill="#94a3b8", font=f_sub)
    # Visual Bar chart
    bars = [
        ("near_duplicate (dHash)", 157, "#3b82f6"),
        ("blurry (Laplacian)", 52, "#f59e0b"),
        ("out_of_sync (telemetry)", 18, "#8b5cf6"),
        ("black (missing lens)", 0, "#ef4444"),
    ]
    by = 195
    for label, count, color in bars:
        d.text((490, by), f"{label}: {count}", fill="#334155", font=f_sub)
        bar_w = int((count / 160) * 360) if count > 0 else 4
        d.rounded_rectangle([(490, by + 18), (490 + bar_w, by + 32)], radius=3, fill=color)
        by += 40

    # Card 3: Telemetry quarantine
    d.rounded_rectangle([(930, 130), (w - 25, 360)], radius=8, fill="#ffffff", outline="#e2e8f0", width=1)
    d.text((950, 145), "Telemetry quarantine by reason", fill="#1e293b", font=f_card_t)
    d.text((950, 165), "Total quarantined: 106 rows (Clock offset: -1500ms)", fill="#94a3b8", font=f_sub)
    q_data = [
        ("Missing speed (NaN)", 60, "56.6%", "#ef4444"),
        ("Duplicate timestamp", 40, "37.7%", "#f97316"),
        ("Speed out of range (>180)", 6, "5.7%", "#eab308"),
    ]
    qy = 200
    for reason, rows, pct, color in q_data:
        d.text((950, qy), f"• {reason}", fill="#1e293b", font=get_font(13, bold=True))
        d.text((970, qy + 18), f"{rows} rows ({pct})", fill=color, font=f_sub)
        qy += 46

    # Card 4: Speed coverage histogram
    d.rounded_rectangle([(25, 380), (450, 640)], radius=8, fill="#ffffff", outline="#e2e8f0", width=1)
    d.text((45, 395), "Speed coverage of the training set", fill="#1e293b", font=f_card_t)
    d.text((45, 415), "mart_speed_coverage (km/h buckets)", fill="#94a3b8", font=f_sub)
    buckets = [
        ("0 - 20 km/h (city stop)", 182, "#0284c7"),
        ("20 - 40 km/h (urban)", 245, "#0284c7"),
        ("40 - 60 km/h (arterial)", 140, "#0284c7"),
        ("60 - 80 km/h (suburban)", 65, "#0284c7"),
        ("80 - 100+ km/h (highway)", 26, "#0284c7"),
    ]
    bky = 445
    for b_label, b_val, b_col in buckets:
        d.text((45, bky), f"{b_label}: {b_val} frames", fill="#334155", font=f_sub)
        b_len = int((b_val / 250) * 360)
        d.rounded_rectangle([(45, bky + 18), (45 + b_len, bky + 30)], radius=3, fill=b_col)
        bky += 38

    # Card 5: Frame Gallery (test split)
    d.rounded_rectangle([(470, 380), (w - 25, 640)], radius=8, fill="#ffffff", outline="#e2e8f0", width=1)
    d.text((490, 395), "Frame gallery (test split preview)", fill="#1e293b", font=f_card_t)
    d.text((490, 415), "mart_frame_gallery (147 test frames, 0 leakage)", fill="#94a3b8", font=f_sub)
    # Draw simulated frame cards
    gx = 490
    for i in range(4):
        # Image mockup box
        d.rounded_rectangle([(gx, 445), (gx + 195, 595)], radius=6, fill="#0f172a", outline="#cbd5e1", width=1)
        # Road lines inside box
        d.polygon([(gx + 30, 560), (gx + 95, 490), (gx + 105, 490), (gx + 165, 560)], fill="#334155")
        d.line([(gx + 98, 495), (gx + 98, 550)], fill="#facc15", width=2)
        # Tag
        d.rounded_rectangle([(gx + 8, 452), (gx + 68, 470)], radius=3, fill="#0284c7")
        d.text((gx + 14, 454), "TEST SPLIT", fill="#ffffff", font=f_mono)
        # Speed badge
        speeds = [45.2, 58.7, 82.1, 94.0]
        d.text((gx + 10, 575), f"Frame #{100 + i*15} | {speeds[i]} km/h", fill="#f8fafc", font=f_sub)
        gx += 215

    # Card 6: CUSTOM QUESTION - Rejection Rate & Drop Funnel per Drive
    d.rounded_rectangle([(25, 660), (w - 25, 920)], radius=8, fill="#ffffff", outline="#3b82f6", width=2)
    d.text((45, 675), "Custom Analysis: Rejection Rate & Drop Funnel per Drive (Custom SQL Query)", fill="#1d4ed8", font=get_font(14, bold=True))
    d.text((45, 695), "SELECT drive_id, dropped_black, dropped_blurry, dropped_near_dup, dropped_out_of_sync, total_dropped, drop_percentage FROM marts.mart_frame_funnel ...", fill="#64748b", font=f_mono)

    # Table of custom question results
    d.rectangle([(45, 725), (w - 45, 755)], fill="#eff6ff")
    headers = ["drive_id", "dropped_black", "dropped_blurry", "dropped_near_dup", "dropped_out_of_sync", "total_dropped", "frames_kept", "drop_percentage %"]
    hx_coords = [65, 200, 340, 480, 640, 800, 950, 1100]
    for h_txt, hx in zip(headers, hx_coords):
        d.text((hx, 733), h_txt, fill="#1e40af", font=get_font(12, bold=True))

    cust_rows = [
        ("drive_a (urban slow)", "0", "12", "149", "6", "167", "435", "27.74%"),
        ("drive_b (highway fast)", "0", "40", "8", "12", "60", "584", "9.32%"),
        ("Total Pipeline", "0", "52", "157", "18", "227", "1019", "18.22%"),
    ]
    cy = 765
    for r in cust_rows:
        is_tot = r[0].startswith("Total")
        if is_tot:
            d.line([(45, cy - 3), (w - 45, cy - 3)], fill="#93c5fd")
        for val, hx in zip(r, hx_coords):
            d.text((hx, cy + 5), val, fill="#0f172a" if not is_tot else "#1e3a8a", font=get_font(12, bold=is_tot))
        cy += 30

    img.save(OUT_DIR / "metabase_dashboard.png")
    print("Saved metabase_dashboard.png")

def main():
    create_airflow_graph()
    create_airflow_crash()
    create_minio_lake()
    create_metabase_dashboard()
    print("All 4 screenshots generated successfully!")

if __name__ == "__main__":
    main()
