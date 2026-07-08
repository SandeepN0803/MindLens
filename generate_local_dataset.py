import csv
import random

categories = {
    'Magnification and Catastrophizing': [
        'My {body_part} felt {symptom} for a second and now I am sure I have a deadly disease.',
        'If this {work_project} fails, my entire {career} is over and I will be {ruined}.',
        'I {mistake} and now my whole {life_aspect} is a complete {disaster}.',
        'The {event} did not go perfectly, so I am convinced the rest of the {time_period} will be terrible.',
        'I got a {grade} on the quiz, I will never graduate and will end up a total failure.',
        'My {relative} {negative_action}, this is the worst possible thing that could happen.',
        'I lost my {item}, I will never be able to function normally again.',
        'There is a {minor_issue} in the {place}, it is going to collapse and we will lose everything.',
        'I felt a little {emotion} today, I am definitely descending into a permanent breakdown.',
        'The {vehicle} made a weird noise, it is definitely going to {bad_event} on the highway.'
    ],
    'Black & White Thinking': [
        'I made one mistake in the {task}, so the whole thing was a complete {failure}.',
        'I either get {perfect_result} on this or I am a total {loser}.',
        'If they do not {positive_action} me completely, then they must {negative_action} me entirely.',
        'My diet is ruined because I ate one {food}, so I might as well eat junk forever.',
        'The {event} was not flawless, so it was a total {disaster}.',
        'I did not finish all my {chores}, so today was completely {unproductive}.',
        'If I am not the absolute best at {skill}, there is no point in even {trying}.',
        'He disagreed with me once, so he is completely {against} me.',
        'I did not win the {competition}, so I am a complete loser.',
        'Either I figure this out right now, or I am completely {incompetent}.'
    ],
    'Jumping to Conclusions': [
        'She did not reply to my text in {time_period}, she must think I am {annoying} now.',
        'I know I am going to bomb this {challenge} no matter how much I {prepare}.',
        'He looked at me funny, he definitely thinks I am an {idiot}.',
        'I know this {event} is going to be terrible before it even starts.',
        'My boss scheduled a {work_project}, they are definitely going to {fire} me.',
        'They are whispering over there, I know they are {laughing} at me.',
        'I am going to fail the {challenge}, I just know it.',
        'The {work_project} will definitely be {rejected}, so why bother.',
        'She canceled our {event}, she obviously {hates} spending time with me.',
        'I have not heard back from the {challenge}, they clearly {rejected} me.'
    ],
    'Overgeneralization': [
        'I forgot her birthday, I {always} mess up the things that matter to people.',
        'I got rejected from this {job}, I will {never} get hired anywhere.',
        'I burned the {food}, I am {always} terrible at {cooking}.',
        'My partner broke up with me, I am {never} going to find {love}.',
        'I tripped on the sidewalk, I am {always} so incredibly {clumsy}.',
        'I failed this {challenge}, I {never} succeed at anything important.',
        'He yelled at me, people are {always} so {mean} to me.',
        'I missed the {vehicle}, nothing {ever} goes right in my life.',
        'I lost the {competition}, I {always} lose everything.',
        'This {device} broke, technology {always} fails me when I need it.'
    ],
    'Personalization': [
        'My {relative} has been quiet lately, it must be something I {did}.',
        'It rained on our {event}, it is all my fault for {planning} it today.',
        'My team lost the {competition}, it is entirely my fault for missing that one {play}.',
        'The {work_project} failed, it is completely because of my minor {mistake_noun}.',
        'My {relative} is in a bad mood, I must have {upset} them.',
        'The {event} was boring, I should have been more {entertaining}.',
        'The {pet} is sick, I must have done something {wrong} to cause it.',
        'My {relative} got passed over for a {job}, I feel guilty like it is my fault.',
        'The economy is bad, I somehow feel responsible for not doing enough.',
        'They got into an argument, it is my fault for {introducing} them.'
    ],
    'Emotional Reasoning': [
        'I feel like a {fraud} at work, so I must actually be bad at my {job}.',
        'I feel so {overwhelmed}, this situation must be impossible to {fix}.',
        'I feel terrified of {phobia}, so they must be inherently {dangerous}.',
        'I feel guilty, so I must have done something truly {terrible}.',
        'I feel {ugly} today, so everyone must think I am hideous.',
        'I feel {stupid} in this class, so I must actually be the dumbest person here.',
        'I feel {hopeless} about the future, so things will never get better.',
        'I feel {lonely} right now, so I must be completely {unlovable}.',
        'I feel jealous, so my partner must be doing something {wrong}.',
        'I feel anxious about the {event}, so it is definitely going to go badly.'
    ],
    'Should Statements': [
        'I {should} be over this {event} by now, there is something wrong with me.',
        'I {must} always be {productive} or I am wasting my life.',
        'People {ought} to always be {polite}, and it infuriates me when they aren\'t.',
        'I {should} not feel {emotion} about this, I need to just get over it.',
        'I {must} never make a {mistake_noun} at work.',
        'He {should} know exactly how I feel without me having to tell him.',
        'I have to {good_habit} every single day or I am a failure.',
        'I {should} have known better, I am so {stupid}.',
        'The world {should} be {fair}, and I cannot handle that it isn\'t.',
        'I {must} always be the {smartest} person in the room.'
    ],
    'Mental Filter': [
        'The review had {positive_count} positive comments and one suggestion, but all I can think about is that one {criticism}.',
        'I had a great day but I dropped my {item}, so today was {ruined}.',
        'I scored {high_score} on the {challenge}, but I am agonizing over the {low_score} I got wrong.',
        'The {event} was beautiful, but it {bad_event} for one hour and that ruined the whole thing.',
        'I got a {job} and a raise, but my boss did not {positive_action} when he told me, so it is awful.',
        'Everyone complimented my {creation}, but one person was quiet, so that person secretly {hates} it.',
        'I won the {competition}, but I did not beat my personal best, so it was a {terrible} performance.',
        'My partner did {positive_count} nice things for me, but forgot to {chores}, so they do not care at all.',
        'The {event} was a success, but the {minor_issue} was slightly off, making it a disaster.',
        'I accomplished everything on my to-do list except one {minor_issue}, so I am completely {unproductive}.'
    ],
    'No Distortion': [
        'Today was busy but manageable. I got most of my {chores} done and had a nice walk.',
        'I made a {mistake_noun} in the {work_project}, but I corrected it and my manager said it was okay.',
        'I feel {emotion} about the {event}, but I know time will heal the wound.',
        'The {event} did not go perfectly, but we learned a lot for next time.',
        'I did not get the {job}, which is disappointing, but I will keep applying.',
        'My {relative} is {emotion}, I will ask if they want to talk about it.',
        'I am feeling {emotion} about the {challenge}, so I am going to prepare for an hour and then rest.',
        'I burned the {food}, so I will just order pizza instead.',
        'I am tired today, so I am going to take it easy tonight.',
        'I disagreed with my {relative}, but we talked it out and came to an understanding.'
    ]
}

fillers = {
    'body_part': ['chest', 'arm', 'head', 'stomach', 'leg', 'eye', 'back', 'neck', 'shoulder'],
    'symptom': ['tight', 'numb', 'dizzy', 'weird', 'painful', 'tingly', 'heavy', 'cold', 'sore'],
    'work_project': ['project', 'presentation', 'report', 'deal', 'meeting', 'code', 'assignment', 'task', 'proposal'],
    'career': ['career', 'future', 'reputation', 'livelihood', 'business', 'job'],
    'ruined': ['ruined', 'destroyed', 'over', 'finished', 'doomed'],
    'mistake': ['spilled coffee', 'sent the wrong email', 'said the wrong thing', 'arrived late', 'forgot my keys', 'broke the glass', 'lost the document'],
    'life_aspect': ['life', 'week', 'month', 'year', 'day', 'evening'],
    'disaster': ['disaster', 'nightmare', 'tragedy', 'catastrophe', 'mess', 'failure'],
    'time_period': ['a year', 'a month', 'a week', 'a day', 'an hour', '10 minutes'],
    'grade': ['B', 'C', 'D', 'F', '85%', '70%', '60%'],
    'relative': ['mom', 'dad', 'sister', 'brother', 'cousin', 'friend', 'partner', 'colleague', 'boss'],
    'negative_action': ['frowned', 'sighed', 'yelled', 'ignored', 'left', 'criticized', 'rejected', 'abandoned'],
    'item': ['phone', 'wallet', 'keys', 'ring', 'watch', 'headphones', 'glasses', 'laptop'],
    'minor_issue': ['creak', 'crack', 'leak', 'draft', 'stain', 'scratch', 'dent'],
    'place': ['house', 'apartment', 'room', 'office', 'building', 'kitchen'],
    'emotion': ['sad', 'anxious', 'angry', 'lonely', 'bored', 'nervous', 'upset', 'frustrated'],
    'vehicle': ['car', 'bike', 'bus', 'train', 'scooter', 'plane'],
    'bad_event': ['explode', 'break down', 'crash', 'fail', 'catch fire', 'rain'],
    'task': ['assignment', 'chore', 'project', 'presentation', 'recipe', 'job'],
    'failure': ['failure', 'waste', 'joke', 'disappointment', 'embarrassment'],
    'perfect_result': ['100%', 'an A+', 'a perfect score', 'first place', 'the best review'],
    'loser': ['loser', 'failure', 'idiot', 'fool', 'disappointment'],
    'positive_action': ['love', 'support', 'help', 'encourage', 'praise', 'smile at'],
    'food': ['cookie', 'slice of pizza', 'donut', 'bag of chips', 'candy bar', 'burger', 'fries'],
    'chores': ['laundry', 'dishes', 'cleaning', 'vacuuming', 'errands', 'cooking'],
    'unproductive': ['unproductive', 'useless', 'wasted', 'pointless', 'ruined'],
    'skill': ['math', 'painting', 'coding', 'writing', 'sports', 'music'],
    'trying': ['trying', 'practicing', 'attempting', 'learning', 'starting'],
    'against': ['against', 'mad at', 'disappointed in', 'hating', 'rejecting'],
    'competition': ['race', 'game', 'match', 'tournament', 'contest', 'award', 'election'],
    'incompetent': ['incompetent', 'useless', 'stupid', 'hopeless', 'incapable'],
    'annoying': ['annoying', 'boring', 'stupid', 'weird', 'unlovable'],
    'challenge': ['interview', 'test', 'exam', 'presentation', 'audition', 'meeting'],
    'prepare': ['prepare', 'study', 'practice', 'try', 'rehearse'],
    'idiot': ['idiot', 'fool', 'failure', 'loser', 'weirdo'],
    'fire': ['fire', 'demote', 'yell at', 'reprimand', 'criticize'],
    'laughing': ['laughing', 'mocking', 'judging', 'gossiping', 'staring'],
    'rejected': ['rejected', 'failed', 'declined', 'dismissed', 'ignored'],
    'hates': ['hates', 'dislikes', 'dreads', 'regrets', 'avoids'],
    'always': ['always', 'constantly', 'continually', 'forever', 'invariably'],
    'never': ['never', 'rarely', 'hardly ever', 'almost never', 'seldom'],
    'job': ['job', 'promotion', 'internship', 'role', 'position', 'opportunity'],
    'cooking': ['cooking', 'baking', 'grilling', 'making food', 'preparing dinner'],
    'love': ['love', 'happiness', 'peace', 'joy', 'a relationship'],
    'clumsy': ['clumsy', 'awkward', 'stupid', 'uncoordinated', 'foolish'],
    'mean': ['mean', 'cruel', 'unfair', 'harsh', 'cold'],
    'ever': ['ever', 'always', 'at all', 'in my life', 'for me'],
    'device': ['laptop', 'phone', 'printer', 'tablet', 'TV', 'computer'],
    'did': ['did', 'said', 'implied', 'caused', 'messed up'],
    'planning': ['planning', 'scheduling', 'organizing', 'arranging', 'choosing'],
    'play': ['play', 'shot', 'pass', 'catch', 'move'],
    'mistake_noun': ['mistake', 'error', 'slip-up', 'blunder', 'typo'],
    'upset': ['upset', 'angered', 'annoyed', 'offended', 'bothered'],
    'entertaining': ['entertaining', 'fun', 'interesting', 'engaging', 'lively'],
    'pet': ['dog', 'cat', 'bird', 'fish', 'hamster'],
    'wrong': ['wrong', 'terrible', 'bad', 'harmful', 'careless'],
    'introducing': ['introducing', 'inviting', 'bringing', 'connecting', 'pairing'],
    'fraud': ['fraud', 'fake', 'imposter', 'phony', 'liar'],
    'overwhelmed': ['overwhelmed', 'stressed', 'panicked', 'trapped', 'suffocated'],
    'fix': ['fix', 'solve', 'escape', 'change', 'improve'],
    'phobia': ['flying', 'spiders', 'heights', 'crowds', 'dogs'],
    'dangerous': ['dangerous', 'deadly', 'terrifying', 'harmful', 'unsafe'],
    'terrible': ['terrible', 'awful', 'horrible', 'evil', 'unforgivable'],
    'ugly': ['ugly', 'fat', 'gross', 'hideous', 'unattractive'],
    'stupid': ['stupid', 'dumb', 'slow', 'foolish', 'ignorant'],
    'hopeless': ['hopeless', 'doomed', 'pointless', 'bleak', 'dark'],
    'lonely': ['lonely', 'isolated', 'abandoned', 'rejected', 'forgotten'],
    'unlovable': ['unlovable', 'unwanted', 'undesirable', 'worthless', 'broken'],
    'should': ['should', 'must', 'ought to', 'have to', 'need to'],
    'must': ['must', 'should', 'have to', 'need to', 'ought to'],
    'productive': ['productive', 'busy', 'working', 'achieving', 'useful'],
    'ought': ['ought', 'should', 'need', 'have', 'must'],
    'polite': ['polite', 'nice', 'kind', 'respectful', 'courteous'],
    'good_habit': ['exercise', 'meditate', 'read', 'clean', 'work'],
    'fair': ['fair', 'just', 'equal', 'right', 'perfect'],
    'smartest': ['smartest', 'best', 'hardest working', 'most successful', 'fastest'],
    'positive_count': ['eight', 'nine', 'ten', 'a dozen', 'twenty'],
    'criticism': ['criticism', 'flaw', 'mistake', 'error', 'negative comment'],
    'high_score': ['98%', '95%', '99%', 'an A', 'a 90'],
    'low_score': ['2%', '5%', '1%', 'the few points', 'the one question'],
    'creation': ['painting', 'song', 'essay', 'code', 'meal', 'design']
}

def generate_sentence(template):
    import re
    matches = re.findall(r'\{([^}]+)\}', template)
    sentence = template
    for match in matches:
        if match in fillers:
            sentence = sentence.replace(f'{{{match}}}', random.choice(fillers[match]))
    return sentence

def main():
    target_per_category = 180
    dataset = []
    
    print('Generating dataset...')
    for category, templates in categories.items():
        generated_for_cat = set()
        attempts = 0
        while len(generated_for_cat) < target_per_category and attempts < 100000:
            template_idx = random.randint(0, len(templates) - 1)
            template = templates[template_idx]
            sentence = generate_sentence(template)
            # Use tuple to store unique sentence and its template ID
            entry_tuple = (sentence, f"{category}_{template_idx}")
            if entry_tuple not in generated_for_cat:
                generated_for_cat.add(entry_tuple)
            attempts += 1
            
        for sentence, t_id in generated_for_cat:
            dataset.append({'text': sentence, 'label': category, 'language': 'en', 'template_id': t_id})
            
        print(f'Generated {len(generated_for_cat)} entries for {category}.')
        assert len(generated_for_cat) >= 100, f'Failed to generate enough entries for {category}! Only got {len(generated_for_cat)}'

    random.shuffle(dataset)
    
    output_file = 'data/synthetic_distortions_en.csv'
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['text', 'distortion_label', 'language', 'template_id'])
        for row in dataset:
            writer.writerow([row['text'], row['label'], row['language'], row['template_id']])
            
    print(f'\\nSuccessfully wrote {len(dataset)} single-label entries to {output_file}.')

if __name__ == '__main__':
    main()
