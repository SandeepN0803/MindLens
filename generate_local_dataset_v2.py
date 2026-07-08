import csv
import random
import re

random.seed(42)

# ==============================================================================
# TEMPLATES
# Each category has:
#   "trigger"     -> templates using an obvious keyword (always/never, ruin,
#                     should/must, hate, etc.) -- capped at 20% of output
#   "non_trigger" -> templates expressing the same distortion without those
#                     words, via situation/logic/tone only
# ==============================================================================

CATEGORIES = {
    "Magnification and Catastrophizing": {
        "trigger": [
            "If this {work_project} fails, it will be an absolute {disaster} and my {career} is finished.",
            "My {body_part} felt {symptom} for a second, this is going to be a total catastrophe.",
            "One {minor_issue} in the {place} and I'm sure the whole thing is going to collapse.",
        ],
        "non_trigger": [
            "My {body_part} has felt a bit {symptom} since this morning. I keep picturing the worst-case scenario in the {place}.",
            "The {vehicle} made a strange sound on the way to {location}, and now I can't stop imagining it breaking down somewhere dangerous.",
            "I got some unexpected news about my {work_project} today, and my mind immediately jumped to losing everything over it.",
            "There's a {minor_issue} in the {place} that I noticed this evening. I lay awake running through everything that could go wrong because of it.",
            "The doctor mentioned my {body_part} looked slightly {symptom} on the scan. I spent the whole drive home assuming the worst.",
            "I missed one {vehicle} connection today, and somehow my brain turned it into 'my whole trip is ruined.'",
            "A single line in the {work_project} feedback stood out to me, and by tonight I'd convinced myself the entire thing would fall apart.",
            "The {place} creaked a little louder than usual tonight and I found myself Googling structural failures at 1am.",
            "Someone at {location} coughed near me and I've already started planning for being seriously ill by next week.",
            "My manager asked to 'chat' about the {work_project} tomorrow, and I've spent the evening assuming it means the worst possible outcome.",
        ],
    },
    "Black & White Thinking": {
        "trigger": [
            "I made one mistake in the {task}, so the whole thing was a complete {failure}.",
            "Either I am the best at {skill}, or there is no point trying at all.",
            "If my {relative} doesn't {positive_action} me completely, then it means they must {negative_action} me entirely.",
        ],
        "non_trigger": [
            "I got through most of the {task} smoothly, but one part didn't go as planned, so by the end of {time_period} I felt like none of it counted.",
            "My {relative} pointed out one thing I could improve on the {creation}, and I stopped seeing anything good in it after that.",
            "The {event} had a lot of nice moments, but the one awkward part at {location} is the only thing I can file it under now.",
            "I ate one thing off my usual routine today, and somehow that turned into skipping the rest of the day's plan for my {chores} entirely.",
            "Halfway through the {competition} I made a small error, and after that I mentally checked out like the outcome was already decided.",
            "My {relative} disagreed with me on one small thing about the {event}, and for the rest of the conversation I felt like we were on completely different sides.",
            "I didn't finish every item on my {chores} list, so tonight feels like a wasted {time_period} even though I got most of it done.",
            "There wasn't a clear right answer in the {challenge}, which somehow made me feel like I'd already failed it completely.",
            "One part of the {work_project} needs revision, and now I keep referring to the whole draft as a {failure}.",
            "I skipped one workout this {time_period} and I've been telling myself the whole {time_period} is a write-off.",
        ],
    },
    "Jumping to Conclusions": {
        "trigger": [
            "My {relative} didn't reply to my text in {time_period}, they must think I'm {annoying} now.",
            "I know I'm going to bomb this {challenge} no matter how much I {prepare}.",
            "My boss scheduled a meeting about the {work_project}, they're definitely going to {fire} me.",
        ],
        "non_trigger": [
            "My {relative} was quieter than usual at dinner. I've been replaying the last {time_period} trying to figure out what I did wrong at {place}.",
            "The {relative} closed the door to their office right as I walked past. I've already decided what that means for my {job}.",
            "I sent the {work_project} update and haven't heard anything back yet. Part of me has already written the ending to this.",
            "Two people were talking quietly by the {place} and glanced over. I spent the rest of the {time_period} assuming it was about me.",
            "I wasn't invited to the {event} this time, and I've built an entire story in my head about why, without asking my {relative}.",
            "The interviewer's expression changed partway through my {challenge}, and I left {location} convinced I already know the outcome.",
            "My {relative} took longer than usual to reply to my message, and I've decided that means something is wrong between us regarding the {event}.",
            "The {relative} seemed distracted during our call about the {work_project}. I've been assuming it's about something I said last {time_period}.",
            "I noticed my name mentioned quietly in the {place} and immediately assumed the worst about what was being said.",
            "The results for the {competition} haven't been posted yet, but I've already told myself how badly it's going to go.",
        ],
    },
    "Overgeneralization": {
        "trigger": [
            "I forgot {relative}'s birthday, I always mess up the things that matter to people.",
            "I got rejected from this {job} after preparing for {time_period}, I will never get hired anywhere.",
            "My {relative} yelled at me, people are always so {negative_action} towards me.",
        ],
        "non_trigger": [
            "I forgot an important date for my {relative} again this year. It's starting to feel like a pattern I can't break, no matter how much I try.",
            "This is the second {challenge} in a row that didn't go anywhere. I'm starting to wonder if this is just how it's going to keep going for my {career}.",
            "My {relative} snapped at me today, and it's made me think back to every other time someone's been short with me lately at {location}.",
            "I burned the {creation} again tonight. Cooking has started to feel like something I'm just not cut out for.",
            "Another {event} ended the same way the last one did. I'm starting to see a theme in how these things go for me and my {relative}.",
            "I tripped in front of a group of people at the {place} today, and it's the third clumsy thing that's happened to me this {time_period} alone.",
            "I missed the deadline for this {task}, and looking back, deadlines have been a recurring struggle for me this whole {time_period}.",
            "The {device} stopped working right when I needed it most for the {work_project}, just like the last three things I've relied on.",
            "I lost the {competition} again, and it's hard not to feel like winning just isn't something that happens for me.",
            "Nothing about today's {event} went the way I planned, and lately it feels like that's just become the norm.",
        ],
    },
    "Personalization": {
        "trigger": [
            "My {relative} has been quiet lately in the {place}, it must be something I did.",
            "It rained on our {event}, it's all my fault for planning it today.",
            "My team lost the {competition}, it's entirely my fault for missing that one play during {time_period}.",
        ],
        "non_trigger": [
            "The {event} didn't go as smoothly as hoped, and I keep replaying my part in it, wondering what I could have done differently.",
            "My {relative} has seemed a bit off this {time_period}, and I've quietly started assuming I'm the reason.",
            "The {work_project} came in under expectations, and even though several people worked on it, I keep centering the blame on my own part.",
            "The {pet} hasn't been eating well at {place}, and I've been wondering what I might have changed that caused it.",
            "My {relative} didn't get the {job} they wanted, and somehow I've attached myself to the reasons why.",
            "The mood at the {event} felt a little flat, and I've spent the ride home from {location} wondering if it was something about how I showed up.",
            "A conversation between two coworkers went quiet when I walked into the {place}, and I've decided it must have been about something I did.",
            "The {event} didn't go as well as planned, and I keep going over my choices as if the whole thing rested on me.",
            "My {relative} and their friend had a falling out recently, and I keep wondering if introducing them was the root of it.",
            "Things felt tense at the {event} today, and I've quietly taken on responsibility for the whole atmosphere.",
        ],
    },
    "Emotional Reasoning": {
        "trigger": [
            "I feel like a fraud at work, so I must actually be bad at my {job}.",
            "I feel so hopeless about the {work_project}, so things will never get better.",
            "I feel guilty about {event}, so I must have done something truly terrible.",
        ],
        "non_trigger": [
            "Something about today's {event} just feels off, and I've been treating that feeling like solid proof that something is actually wrong.",
            "I've had a knot in my stomach all {time_period} about the {challenge}, and it's hard not to take that as a sign of how it's going to go.",
            "I don't feel ready for the {event}, and that feeling alone has convinced me I'm not actually ready.",
            "There's a heaviness I can't shake tonight in the {place}, and I keep assuming it means something bad is coming to my {career}.",
            "I feel disconnected from my {relative} right now, which makes it hard to believe that anyone actually wants me around at {location}.",
            "My gut has been uneasy about the {work_project} all {time_period}, and I've stopped questioning whether that unease is accurate.",
            "I feel like I don't belong in this {place}, and that feeling has quietly become the whole story I believe about myself here.",
            "The anxiety before the {challenge} feels like a warning, so I've been treating it as one.",
            "I feel exhausted just thinking about the {task}, and that tiredness has turned into a belief that I simply can't do it.",
            "Something in me feels certain the {competition} will go badly, even though I can't point to a single real reason why.",
        ],
    },
    "Should Statements": {
        "trigger": [
            "I should be over this {event} by now, there's something wrong with me for still feeling this way after {time_period}.",
            "I must always be productive with my {task} or I'm wasting my life.",
            "My {relative} ought to always be polite, and it infuriates me when they aren't.",
        ],
        "non_trigger": [
            "It's been a while since the {event}, and I keep expecting myself to have moved past it by now.",
            "I spent the {time_period} resting instead of working on the {task}, and I can't shake the feeling that I wasted the time.",
            "My {relative} didn't react the way I expected after everything I did for them at the {event}, and I keep stewing over how unfair that feels.",
            "I keep holding myself to a version of this {job} where I never make a single {mistake_noun}, and falling short of that eats at me.",
            "I expect to handle the {challenge} calmly every time, and getting nervous about it tonight feels like a personal failure.",
            "There's a version of how the {event} was 'supposed' to go, and tonight in the {place} I can't stop measuring reality against it.",
            "I hold a pretty rigid picture of how a good {job} looks, and today didn't come close to matching it.",
            "I keep thinking I need to have this all figured out by now, and not having answers about my {career} yet feels like falling behind some invisible schedule.",
            "My {relative} handled the {event} differently than I would have, and it's been bothering me all {time_period} that they didn't do it 'right.'",
            "I hold myself to never showing I'm struggling with the {task}, and today at {location} I couldn't keep that up.",
        ],
    },
    "Mental Filter": {
        "trigger": [
            "The review for the {work_project} had nine positive comments and one suggestion, but all I can think about is that one criticism.",
            "Everyone complimented my {creation}, but my {relative} was quiet, so they must secretly hate it.",
            "I won the {competition}, but I didn't beat my personal best, so it was a {failure} performance.",
        ],
        "non_trigger": [
            "The {event} went well overall, but there's a small moment from it with my {relative} that I keep replaying instead of anything else.",
            "I got through most of the {task} without issue, but the one snag is what's stuck with me all {time_period}.",
            "People seemed to enjoy the {creation}, but I keep circling back to the single comment that wasn't glowing.",
            "The {work_project} feedback was mostly encouraging, yet somehow it's the one line of critique that's occupying my whole evening at {place}.",
            "My {relative} said a lot of kind things today, but there's one offhand remark that's the only part I can remember clearly.",
            "The {competition} results were solid, but I keep zeroing in on the single category where I placed lower.",
            "Almost everything about the trip to {location} went smoothly, except for one hiccup that's somehow become the whole story I tell about it.",
            "The {event} was full of good moments, but my mind keeps returning to the one that didn't land.",
            "I got mostly positive feedback on the {creation}, but the single hesitant comment from my {relative} is the only one I can actually recall.",
            "The day had plenty of wins at {location}, but there's one small thing about the {task} that went wrong that I can't seem to let go of.",
        ],
    },
    "No Distortion": {
        "trigger": [
            "I made a {mistake_noun} in the {work_project}, but I corrected it and my manager said it was fine.",
            "I didn't get the {job}, which is a disappointment, but I'll keep applying.",
            "I disagreed with my {relative}, but we talked it out over {time_period} and came to an understanding.",
        ],
        "non_trigger": [
            "Today at {location} was a mix of good and less-good moments, and that feels pretty normal to me.",
            "The {event} didn't go exactly as planned, but there were some genuinely nice parts too.",
            "I'm a little tired after the {task}, so I'm going to take it easy in the {place} tonight and pick things back up tomorrow.",
            "My {relative} and I saw things differently about the {event}, but we were able to talk it through calmly.",
            "The {competition} didn't go my way this time, but I can see a few things I'll try differently next time.",
            "I felt nervous before the {challenge}, so I gave myself some time to prepare and it went reasonably well.",
            "The {work_project} isn't perfect, but I think it's in a solid place given the time we had.",
            "I'm feeling a bit off today, so I'm planning a quieter {time_period} and will check in with myself tomorrow.",
            "The {creation} turned out differently than I first imagined, but I'm still glad I made it.",
            "It's been an ordinary week -- some things went well at {location}, a couple of things didn't, and that's alright.",
        ],
    },
}

FILLERS = {
    "body_part": ["chest", "arm", "head", "stomach", "leg", "eye", "back", "neck", "shoulder", "wrist", "knee"],
    "symptom": ["tight", "numb", "dizzy", "weird", "painful", "tingly", "heavy", "cold", "sore", "stiff", "warm"],
    "work_project": ["project", "presentation", "report", "deal", "meeting", "code", "assignment", "proposal", "pitch", "budget review"],
    "career": ["career", "future", "reputation", "livelihood", "standing at work"],
    "disaster": ["disaster", "nightmare", "catastrophe", "mess"],
    "minor_issue": ["creak", "crack", "leak", "draft", "stain", "scratch", "dent", "flicker"],
    "place": ["house", "apartment", "office", "building", "kitchen", "garage", "basement"],
    "vehicle": ["car", "bike", "bus", "train", "scooter"],
    "location": ["work", "the airport", "the gym", "school", "the store", "the clinic"],
    "task": ["assignment", "chore", "project", "presentation", "recipe", "report", "cleanup"],
    "failure": ["failure", "waste", "disappointment", "embarrassment"],
    "skill": ["math", "painting", "coding", "writing", "sports", "music", "public speaking"],
    "positive_action": ["love", "support", "encourage", "praise"],
    "negative_action": ["resent", "reject", "dislike", "avoid"],
    "relative": ["mom", "dad", "sister", "brother", "cousin", "friend", "partner", "colleague", "boss", "roommate"],
    "creation": ["painting", "song", "essay", "code", "meal", "design", "presentation", "photo"],
    "event": ["party", "trip", "dinner", "wedding", "concert", "reunion", "outdoor event", "gathering"],
    "competition": ["race", "game", "match", "tournament", "contest", "audition", "election"],
    "chores": ["laundry", "dishes", "cleaning", "vacuuming", "errands", "cooking", "yard work"],
    "challenge": ["interview", "test", "exam", "presentation", "audition", "meeting", "performance review"],
    "prepare": ["prepare", "study", "practice", "rehearse"],
    "time_period": ["a day", "a few hours", "a week", "an afternoon"],
    "annoying": ["annoying", "boring", "difficult", "too much"],
    "job": ["job", "promotion", "internship", "role", "position", "opportunity"],
    "pet": ["dog", "cat", "bird", "fish", "hamster"],
    "device": ["laptop", "phone", "printer", "tablet", "router", "car"],
    "mistake_noun": ["mistake", "error", "slip-up", "oversight", "typo"],
    "fire": ["fire", "demote", "reprimand", "let go"],
}


def fill(template: str) -> str:
    matches = re.findall(r"\{([^}]+)\}", template)
    sentence = template
    for m in matches:
        if m in FILLERS:
            sentence = sentence.replace(f"{{{m}}}", random.choice(FILLERS[m]), 1)
    return sentence


def generate_category(category: str, spec: dict, target_total: int) -> list[dict]:
    """Generate rows for one category, capping trigger-template rows at 20% of target."""
    max_trigger = max(1, round(target_total * 0.20))
    rows = []
    seen = set()

    # non-trigger rows first (the bulk)
    non_trigger_target = target_total - max_trigger
    attempts = 0
    while len([r for r in rows if r["source"] == "non_trigger"]) < non_trigger_target and attempts < 20000:
        template = random.choice(spec["non_trigger"])
        text = fill(template)
        key = text.lower().strip()
        if key not in seen:
            seen.add(key)
            rows.append({"text": text, "label": category, "source": "non_trigger", "template": template})
        attempts += 1

    # trigger rows, capped
    attempts = 0
    while len([r for r in rows if r["source"] == "trigger"]) < max_trigger and attempts < 20000:
        template = random.choice(spec["trigger"])
        text = fill(template)
        key = text.lower().strip()
        if key not in seen:
            seen.add(key)
            rows.append({"text": text, "label": category, "source": "trigger", "template": template})
        attempts += 1

    return rows


def main():
    target_per_category = 180
    all_rows = []

    print("Generating enhanced local dataset (v2)...")
    for category, spec in CATEGORIES.items():
        rows = generate_category(category, spec, target_per_category)
        trigger_count = sum(1 for r in rows if r["source"] == "trigger")
        print(f"  {category}: {len(rows)} rows ({trigger_count} trigger, {len(rows) - trigger_count} non-trigger)")
        assert len(rows) >= 100, f"Failed to generate enough rows for {category}: only {len(rows)}"
        all_rows.extend(rows)

    random.shuffle(all_rows)

    output_file = "data/synthetic_distortions_en_v2.csv"
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "distortion_label", "language", "template_id"])
        for row in all_rows:
            # template_id groups rows generated from the same template, for GroupShuffleSplit
            template_id = f"{row['label']}::{hash(row['template']) % 100000}"
            writer.writerow([row["text"], row["label"], "en", template_id])

    print(f"\nWrote {len(all_rows)} rows to {output_file}")


if __name__ == "__main__":
    main()
