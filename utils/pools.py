"""Extra content pools for the unlimited question generators. Teachers can add lines freely.

All names are gender-neutral; situations avoid party politics, religion and stereotypes.
"""

NAMES = ["Kiran", "Sam", "Alex", "Robin", "Ash", "Ari", "Jo", "Dev", "Noel", "Sasha", "Ray", "Charu"]

# (statement, label) label: 0 fact, 1 opinion, 2 assumption, 3 overgeneralisation
MORE_STATEMENTS = [
    ("The bridge was closed for repairs on 3 March.", 0), ("The college canteen sells tea for ₹10.", 0),
    ("The district recorded 42 cm of rain in June, according to the weather department.", 0),
    ("The exam timetable was published on the university website on Monday.", 0),
    ("Our town's bus stand has four platforms.", 0), ("The museum is closed on public holidays.", 0),
    ("The new hostel has 120 rooms.", 0), ("The panchayat meeting started at 10 am and ended at 1 pm.", 0),
    ("Rain is the best weather for studying.", 1), ("Classical music is more meaningful than film music.", 1),
    ("The new library design looks ugly.", 1), ("Football is more exciting than cricket.", 1),
    ("Morning classes are better than afternoon classes.", 1), ("This novel is the most moving book of the decade.", 1),
    ("That speaker was the most inspiring guest we've had.", 1), ("Short videos are a waste of time.", 1),
    ("He wears glasses, so he must study a lot.", 2), ("The shop has no customers today, so it must be closing down.", 2),
    ("She didn't come to the party, so she must dislike us.", 2), ("The app is popular, so it must be safe.", 2),
    ("The teacher gave a hard test, so the teacher wants us to fail.", 2), ("That road is new, so it won't flood.", 2),
    ("They live in a big house, so they never worry about money.", 2), ("The product is expensive, so it must be high quality.", 2),
    ("The speaker has a foreign degree, so everything they say is correct.", 2), ("He smiled, so he must agree with me.", 2),
    ("All hostel food is tasteless.", 3), ("Young people don't respect traditions anymore.", 3),
    ("Every engineering student is good at maths.", 3), ("People who live in cities are always busy.", 3),
    ("Every online review is fake.", 3), ("Shy people never become leaders.", 3), ("All advertisements lie.", 3),
    ("Nobody reads newspapers these days.", 3), ("Every group project ends in a fight.", 3),
    ("Everyone who uses social media is addicted to it.", 3),
]

MORE_FALLACY = {
    "Appeal to popularity": [
        "'Most of my class believes in lucky pens, so they must improve marks.'",
        "'This shampoo is India's number one seller, so it's the best for your hair.'",
        "'The whole village thinks the new tower causes headaches, so it must be true.'",
        "'Everybody skips the reading list, so the readings aren't important.'",
    ],
    "False choice": [
        "'Either we have exams every week, or students will stop studying.'",
        "'You either love this city or you are against it.'",
        "'Either the college buys new computers, or we'll be stuck in the past.'",
        "'If you're not with us on this protest, you're against students.'",
    ],
    "Attacking the person": [
        "'Ignore Robin's suggestion about the timetable — Robin is always on the phone.'",
        "'Why trust Ash's research on water quality? Ash isn't even from this town.'",
        "'Dev's idea for the fest can't be good; Dev failed last year.'",
        "'You can't talk about saving money — you just bought new shoes.'",
    ],
    "Hasty generalisation": [
        "'My first two lab experiments failed, so I'm useless at science.'",
        "'Two students from that college were rude to me, so that college's students are rude.'",
        "'I read one bad review, so that restaurant is terrible.'",
        "'Our team lost two matches, so we'll never win.'",
    ],
    "Slippery slope": [
        "'If we let students wear casual clothes on Friday, soon nobody will follow any rules.'",
        "'If I miss one class, I'll miss all of them and fail the year.'",
        "'If the canteen adds one healthy item, they'll soon remove all the snacks we like.'",
        "'If we allow phones at lunch, soon students will use them in exams.'",
    ],
    "Irrelevant authority": [
        "'A famous footballer says this coaching centre is the best, so I'll join.'",
        "'My favourite singer says this phone has the best camera, so it must be true.'",
        "'A popular quiz-show host says this herbal mix cures fever.'",
        "'An actor in an advertisement says this cement is the strongest.'",
    ],
}

MORE_CORRELATIONS = [
    ("neighbourhoods with more street lights", "fewer reported thefts", "busier, wealthier areas may get both more lights and more police patrols"),
    ("students who sit near the window", "higher creativity scores", "students who choose window seats may already prefer creative activities"),
    ("families who eat dinner together", "children with better school results", "family time and stable routines may support both"),
    ("towns with more bookshops", "higher literacy rates", "education levels may increase both"),
    ("people who carry umbrellas", "wet streets", "rain causes both"),
    ("students who use more highlighters", "longer study hours", "students who study longer may simply use more stationery"),
    ("countries with more mobile phones", "longer life expectancy", "wealth may increase both"),
    ("villages with more ponds", "more mosquito-borne illness", "standing water and warm climate may affect both, alongside sanitation"),
    ("workers who drink tea at work", "fewer sick days", "workplaces with tea breaks may also have better working conditions"),
    ("students who join debate clubs", "better exam essays", "students interested in writing may choose debate"),
    ("shops that play music", "higher sales", "larger, busier shops may play music and also sell more"),
    ("cities with more parks", "lower stress levels", "wealthier cities may afford both parks and better services"),
]

MORE_CONNECTIVES = [
    ("The volunteers worked all night.", "the relief camp was ready by morning.", "As a result"),
    ("Kiran prepared carefully for the debate.", "Kiran forgot the main point on stage.", "However"),
    ("Many fish species depend on mangroves.", "young prawns shelter among their roots.", "For example"),
    ("The new rule saves paper.", "it saves teachers' time.", "In addition"),
    ("The match was cancelled.", "the ground was flooded.", "This is because"),
    ("The app promised privacy.", "it shared location data with advertisers.", "However"),
    ("Prices of onions rose sharply.", "many families bought fewer vegetables.", "As a result"),
    ("Some claims online are hard to check.", "a 'secret study' with no name cannot be verified.", "For example"),
    ("The library extended its hours.", "it opened a quiet reading room.", "In addition"),
    ("Robin missed the bus.", "the road was blocked by a fallen tree.", "This is because"),
    ("The town built a sea wall.", "erosion moved to the next village.", "However"),
    ("The water filter broke.", "students bought bottled drinks.", "As a result"),
    ("Many apps track location.", "a calculator app may ask for GPS access.", "For example"),
    ("The scholarship covers fees.", "it provides money for books.", "In addition"),
    ("Sam couldn't speak at the meeting.", "Sam had lost their voice.", "This is because"),
    ("The speech sounded confident.", "it gave no evidence for its main claim.", "However"),
    ("More people cycled to work.", "traffic near the market reduced.", "As a result"),
    ("Some green claims are hard to trust.", "a 'natural' label tells you very little.", "For example"),
    ("The workshop taught first aid.", "it covered basic fire safety.", "In addition"),
    ("The exam was postponed.", "the university server crashed.", "This is because"),
]

MORE_HEDGES = [
    ("Students who use AI never learn anything.", "Students who rely heavily on AI may miss chances to practise some skills."),
    ("Every rule in college is pointless.", "Some college rules may not achieve their goals and could be reviewed."),
    ("Plastic is always the worst choice.", "Single-use plastic is often harmful, though alternatives also have environmental costs."),
    ("Nobody in our town cares about the river.", "Many people in our town may not be aware of the river's problems."),
    ("Exams always measure intelligence.", "Exams can measure some kinds of knowledge, but not every ability."),
    ("All forwarded messages are lies.", "Many forwarded messages are unverified, so they are worth checking."),
    ("Group work is always unfair.", "Group work can be unfair when tasks are not shared clearly."),
    ("Everyone hates the new timetable.", "Several students have raised concerns about the new timetable."),
    ("Tourists completely destroy local culture.", "Tourism can change local culture in some ways, both positive and negative."),
    ("Scientists are never wrong.", "Scientific findings are usually reliable, and they are revised when new evidence appears."),
    ("Old buildings are always unsafe.", "Some old buildings may need safety checks."),
    ("Online friends are never real friends.", "Online friendships can be meaningful, though they differ from in-person ones."),
]

MORE_SOURCES = [
    ("The official results page of the university", "A blurry photo of a results list shared on social media"),
    ("A fact-check article that links to original documents", "A meme with a quotation and no source"),
    ("A government census report", "An estimate from an anonymous online forum"),
    ("A textbook written by subject experts and reviewed by others", "A random website with no author or date"),
    ("A hospital's official statement with a named spokesperson", "A voice note from an unknown person"),
    ("A product's independent safety certificate", "The product's own advertisement"),
    ("A local news report quoting named residents and officials", "A trending hashtag with no details"),
    ("A study that explains its method and sample size", "A video titled 'SHOCKING TRUTH they hide from you'"),
]

MORE_MISSING = [
    ("A gym says its programme helps students 'lose weight fast'.", "How was this measured, and is the method safe and healthy?"),
    ("The college says the new attendance app is 'secure'.", "What data does it collect, where is it stored, and who can see it?"),
    ("A company says its solar lamps 'last forever'.", "What is the tested battery life, and is there a warranty?"),
    ("A survey says '90% of students love the new menu'.", "How many students were asked, and how were they chosen?"),
    ("A leader says the new market 'will benefit everyone'.", "Who might lose out, such as existing street vendors?"),
    ("An advert says a course 'guarantees a job'.", "What percentage of past students actually got jobs, and what kind?"),
    ("A town says its river clean-up was 'a huge success'.", "What were the water-quality measurements before and after?"),
    ("A website says a new phone 'never overheats'.", "Under what conditions was it tested, and by whom?"),
]
MISSING_DISTRACTORS = ["What colour is the logo?", "Who is the brand ambassador?", "How many social media followers do they have?",
                       "Is the launch event on a weekend?", "What font is used in the advertisement?", "Is the office air-conditioned?",
                       "How tall is the building?", "What music plays in their advertisement?"]

MORE_VOICES = [
    ("The college canteen committee, made only of staff, sets new food prices.", "Students who buy food every day"),
    ("A company decides to move its factory near a village.", "Villagers whose land, water and air may be affected"),
    ("Parents decide which college course their child must study.", "The student who will study the course"),
    ("A housing society decides to cut the trees in its compound.", "Residents who use the shade, and nearby neighbours"),
    ("Tour operators plan new boat routes on a lake.", "Fishing families who use the same waters"),
    ("A university redesigns its website without testing it.", "Students with visual impairments who use screen readers"),
    ("A town plans a festival in the main street.", "Shopkeepers and residents who live and work on that street"),
    ("A school chooses a new online learning platform.", "Students without home internet"),
]
VOICE_DISTRACTORS = ["The decision-makers themselves", "A journalist in another city", "The company's advertising agency",
                     "The printer of the notice", "The software designer", "A celebrity guest"]

# (claim, strongest evidence, [weaker evidence])
EVIDENCE_SETS = [
    ("The new bus route has reduced late-coming.", "Late arrivals fell from 60 to 25 per week in the month after the route began, while other factors stayed the same.",
     ["The bus driver says students look happier.", "The bus is new and looks modern.", "A student posted that the route is 'awesome'."]),
    ("Mangrove planting reduced coastal erosion here.", "Measurements show the shoreline lost 2 m a year before planting and 0.3 m a year after, compared with no change in an unplanted stretch.",
     ["Mangroves look beautiful.", "A tourist said the beach seems wider.", "The planting ceremony was well attended."]),
    ("The reading club improves students' vocabulary.", "Members' vocabulary test scores rose more than non-members' over the same term, with similar starting scores.",
     ["The club meets in a nice room.", "Members say they enjoy the books.", "The club has a large social media following."]),
    ("The awareness campaign reduced plastic waste on campus.", "Daily waste audits show plastic waste fell by a third compared with the same weeks last year.",
     ["The posters were colourful.", "The principal praised the campaign.", "Many students liked the campaign video."]),
    ("The new filter makes the water safer.", "Lab tests before and after installation show bacteria levels dropped below the safety limit.",
     ["The water tastes better to some people.", "The filter is from a famous brand.", "The filter was expensive."]),
    ("The helpline is helping students.", "Anonymous surveys show 70% of callers found it useful, and counselling referrals doubled.",
     ["The helpline number is printed on every notice board.", "The helpline has a catchy name.", "Staff say they are very busy."]),
    ("Flexible deadlines reduced student stress.", "Stress survey scores fell compared with the previous term, while marks stayed similar.",
     ["Students cheered when it was announced.", "One student said it was a relief.", "Teachers liked the idea."]),
    ("The street-light project made the road safer.", "Police records show night-time accidents fell from 14 to 5 in a year, with traffic levels unchanged.",
     ["The lights are LED.", "Residents feel the road is brighter.", "The project was finished on time."]),
]

# (claim, strongest counterargument, [weak responses])
COUNTER_SETS = [
    ("Attendance should not be compulsory in college.", "Some students may fall behind without the structure attendance provides, and class discussions depend on people being present.",
     ["Students who say this are lazy.", "Attendance has always been compulsory.", "I don't like this idea."]),
    ("All college notices should be online only.", "Students without reliable internet or devices could miss important information.",
     ["Paper is old-fashioned.", "Notices are boring anyway.", "The person suggesting this doesn't use the internet."]),
    ("Tourism is always good for local communities.", "Tourism can raise prices and strain water and waste systems, and profits may go mainly to outside companies.",
     ["Tourists are annoying.", "Some tourists are rude.", "I don't travel much."]),
    ("Students should choose all their own subjects.", "Some foundational subjects are needed for later courses, and students may not yet know what they'll need.",
     ["Students are too young to decide anything.", "Teachers know best, always.", "That's not how it works here."]),
    ("Cars should be banned from the town centre.", "People with disabilities, elderly residents and delivery workers may depend on vehicle access.",
     ["Cars are great.", "I like driving.", "The person who said this owns a bicycle shop."]),
    ("Group marks should be the same for all members.", "Members who contribute much less would receive the same credit, which may feel unfair and reduce effort.",
     ["Group work is useless.", "Some people are lazy by nature.", "Marks don't matter."]),
    ("Every student should have to volunteer for 50 hours.", "Students who work part-time or care for family may not have the time without support or flexibility.",
     ["Volunteering is boring.", "Nobody wants to volunteer.", "The college just wants free labour, obviously."]),
    ("Phones should be allowed during exams for dictionary use.", "Phones could also be used to access answers, which would make the exam unfair and hard to supervise.",
     ["Phones are bad.", "Exams have always banned phones.", "Students can't be trusted ever."]),
]

# (situation, correct conflict, [distractors])
VALUE_SETS = [
    ("A friend asks you to keep a secret that their exam answers were copied.", "Loyalty vs honesty", ["Freedom vs privacy", "Respect vs compassion", "Justice vs freedom"]),
    ("A journalist wants to publish a leaked medical record of a public figure.", "Public interest vs privacy", ["Loyalty vs honesty", "Compassion vs responsibility", "Respect vs loyalty"]),
    ("A neighbour wants to play loud music at a family celebration late at night.", "Freedom vs others' wellbeing", ["Honesty vs loyalty", "Justice vs privacy", "Compassion vs honesty"]),
    ("A doctor must decide whether to tell a scared patient a difficult diagnosis now or later.", "Honesty vs compassion", ["Freedom vs justice", "Loyalty vs freedom", "Privacy vs responsibility"]),
    ("A manager must choose between promoting a long-time friend and a more qualified newcomer.", "Loyalty vs fairness", ["Privacy vs honesty", "Freedom vs compassion", "Respect vs freedom"]),
    ("Parents want to read their teenager's messages to keep them safe.", "Safety vs privacy", ["Justice vs loyalty", "Honesty vs freedom", "Fairness vs compassion"]),
    ("A student sees a friend shoplifting a small item.", "Loyalty vs honesty", ["Freedom vs respect", "Privacy vs compassion", "Justice vs freedom"]),
    ("A town must decide whether to allow a factory that brings jobs but pollutes a stream.", "Economic need vs environmental protection", ["Loyalty vs privacy", "Honesty vs respect", "Freedom vs loyalty"]),
]

# (decision, long-term consequence, [short-term or unrelated])
FUTURE_SETS = [
    ("A town fills its lakes to build more houses.", "More flooding and water shortages in later years", ["More houses this year", "Builders get work immediately", "New roads are built quickly"]),
    ("A student skips sleep every night to finish assignments.", "Health and concentration problems building up over the semester", ["More assignments finished this week", "More free time on weekends", "Higher marks tomorrow"]),
    ("A company cuts training budgets to raise profits.", "Less skilled staff and lower quality in future years", ["Higher profits this quarter", "Fewer meetings this month", "A happier finance team this year"]),
    ("A college delays repairing a leaking roof to save money.", "Bigger structural damage and higher repair costs later", ["Money saved this year", "No construction noise this term", "Fewer contractors on campus now"]),
    ("A family uses all savings on a big wedding.", "Less financial security for emergencies in later years", ["A grand celebration this month", "Happy guests this week", "Lots of photos now"]),
    ("A farmer uses heavy chemical fertiliser every season.", "Declining soil health and pollution of water over time", ["Bigger harvest this season", "Quicker growth this month", "Less weeding this week"]),
]

# (text, reasonable inference, [over-inferences])
INFERENCE_SETS = [
    ("The canteen ran out of food by 12:30 every day this week, and queues were longer than usual.",
     "More people than expected are eating at the canteen this week.", ["The canteen staff are lazy.", "The food is the best in the city.", "The canteen will close next week."]),
    ("Robin carried an umbrella and wore boots to college, though the sky was clear.",
     "Robin may have expected rain later or come from an area where it was raining.", ["Robin is strange.", "Robin wants attention.", "Robin doesn't know how to dress."]),
    ("Library visits doubled in the two weeks before exams.",
     "Many students use the library more when exams are close.", ["Students only care about marks.", "The library is popular all year.", "Students hate studying at home."]),
    ("The new app had many downloads in its first week but few users after a month.",
     "Many people tried the app but did not keep using it.", ["The app is a scam.", "Everyone hated the app.", "The developers are bad at their jobs."]),
    ("Fewer migratory birds have visited the wetland in the last three years.",
     "Something about the wetland or the birds' route may have changed and is worth investigating.", ["The birds are extinct.", "Tourists scared all birds away.", "The birds don't like this country anymore."]),
    ("A classmate who was always cheerful has been quiet and missing classes for two weeks.",
     "Something may be troubling them, and it could help to check in kindly.", ["They are angry with the class.", "They've become arrogant.", "They want to drop out."]),
]

# Templated short-writing prompts (claim, skill)
DEBATE_CLAIMS = [
    "Mobile phones should be banned in college classrooms.", "Every college should have a compulsory environmental studies project.",
    "Students should evaluate their teachers anonymously.", "Online exams are as fair as offline exams.",
    "Cities should make public transport free.", "Homework helps learning more than it harms well-being.",
    "College fests should be plastic-free even if costs rise.", "Social media does more good than harm for students.",
    "Every student should learn a third language.", "AI tools should be allowed for brainstorming assignments.",
    "Tourism should be limited in fragile ecosystems.", "College canteens should only sell healthy food.",
    "Internships should be paid.", "Uniforms should be optional in college.", "Group projects should be marked individually.",
]
WRITE_TEMPLATES = [
    ("counterargument", 2, "Claim: '{c}'", "In 4–5 sentences: Give the strongest argument FOR and the strongest argument AGAINST this claim."),
    ("perspectives", 2, "Claim: '{c}'", "In 4–5 sentences: How might a student, a teacher and a parent each see this claim differently?"),
    ("evidence", 3, "Claim: '{c}'", "In 4–5 sentences: What evidence would you need to decide whether this claim is a good idea? Where would you find it?"),
    ("reflection", 3, "Claim: '{c}'", "In 4–5 sentences: State your view with one reason, then say what new information would change your mind."),
    ("logic", 1, "Claim: '{c}'", "In 4–5 sentences: Do you agree? Give one clear reason using 'because'."),
    ("assumptions", 1, "Claim: '{c}'", "In 4–5 sentences: What is one assumption hidden in this claim?"),
]
