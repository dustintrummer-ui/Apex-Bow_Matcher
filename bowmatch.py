import sqlite3

DB_PATH = "bowsDB.db"


def score_candidate(candidate, target_ata, target_brace, ata_tolerance, brace_tolerance):
    candidate_ata = candidate[3]
    candidate_brace = candidate[4]

    ata_diff = abs(candidate_ata - target_ata)
    brace_diff = abs(candidate_brace - target_brace)

    ata_score = 10 * (1 - ata_diff / ata_tolerance)
    brace_score = 10 * (1 - brace_diff / brace_tolerance)

    final_score = 80 + ata_score + brace_score

    return round(final_score, 1)


def find_similar_bows(model, year, ata_tolerance=1.0, brace_tolerance=0.5, min_year=None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    SELECT 
        year,
        variant,
        model,
        ata_length_in,
        brace_height_in,
        mass_weight_lbs,
        draw_length_min_in,
        draw_length_max_in,
        draw_weight_min_lbs,
        draw_weight_max_lbs,
        ibo_speed_fps
    FROM bow_specs
    WHERE model = ?
    AND year = ?
    """, (model, year))

    results = cur.fetchall()

    if not results:
        conn.close()
        return []

    target = results[0]

    target_year = target[0]
    target_model = target[2]
    target_ata = target[3]
    target_brace = target[4]
    target_dl_min = target[6]
    target_dl_max = target[7]
    target_dw_min = target[8]
    target_dw_max = target[9]
    target_ipo_speed = target[10]
    
    if min_year is None:
        min_year = target_year

    lower_ata = target_ata - ata_tolerance
    upper_ata = target_ata + ata_tolerance

    lower_brace = target_brace - brace_tolerance
    upper_brace = target_brace + brace_tolerance

    cur.execute("""
    SELECT 
        bs.year,
        m.name,
        bs.model,
        bs.ata_length_in,
        bs.brace_height_in,
        bs.mass_weight_lbs,
        bs.draw_length_min_in,
        bs.draw_length_max_in,
        bs.draw_weight_min_lbs,
        bs.draw_weight_max_lbs,
        bs.ibo_speed_fps
    FROM bow_specs bs JOIN manufactures m on bs.manufacturer_id = m.manufacturer_id
    WHERE model != ?
    AND bs.ata_length_in BETWEEN ? AND ?
    AND bs.brace_height_in BETWEEN ? AND ?
    AND bs.draw_length_min_in <= ?
    AND bs.draw_length_max_in >= ?
    AND bs.draw_weight_min_lbs <= ?
    AND bs.draw_weight_max_lbs >= ?
    AND bs.year >= ?
    AND bs.ata_length_in IS NOT NULL
    AND bs.brace_height_in IS NOT NULL
    """, (
        target_model,
        lower_ata,
        upper_ata,
        lower_brace,
        upper_brace,
        target_dl_max,
        target_dl_min,
        target_dw_max,
        target_dw_min,
        min_year
    ))

    candidates = cur.fetchall()
    conn.close()

    scored_matches = []

    for candidate in candidates:
        score = score_candidate(
            candidate,
            target_ata,
            target_brace,
            ata_tolerance,
            brace_tolerance
        )

        scored_matches.append({
            "score": score,
            "year": candidate[0],
            "brand": candidate[1],
            "model": candidate[2],
            "ata_length_in": candidate[3],
            "brace_height_in": candidate[4],
            "mass_weight_lbs": candidate[5],
            "draw_length_min_in": candidate[6],
            "draw_length_max_in": candidate[7],
            "draw_weight_min_lbs": candidate[8],
            "draw_weight_max_lbs": candidate[9],
            "ibo_speed_fps": candidate[10]
        })

    scored_matches.sort(key=lambda x: x["score"], reverse=True)

    target_dict={
        "year": target[0],
        "model": target[2],
        "ata_length_in": target[3],
        "brace_height_in": target[4],
        "mass_weight_lbs": target[5],
        "draw_length_min_in": target[6],
        "draw_length_max_in": target[7],
        "draw_weight_min_lbs": target[8],
        "draw_weight_max_lbs": target[9],
        "ibo_speed_fps": target[10]
    }
    return target_dict, scored_matches[:10]


if __name__ == "__main__":
    matches = find_similar_bows("TurboHawk", 2010)

    for match in matches:
        print(match)