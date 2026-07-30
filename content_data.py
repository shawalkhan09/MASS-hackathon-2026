# -*- coding: utf-8 -*-
"""
Content data for the Business Frameworks & Terms reference set.
Each term: number, name, definition, when_to_use, steps (list of strings), example.
Organized into the four tiers from the source request document.
"""

TIER1 = {
    "tier_label": "Tier 1",
    "tier_title": "Core Diagnostic Frameworks",
    "tier_note": "Frameworks the AI applies directly to diagnose a business problem.",
    "terms": [
        {
            "number": 1,
            "name": "Root Cause Analysis (5 Whys)",
            "definition": (
                "A simple, iterative questioning technique that traces a problem back through its "
                "chain of causes by repeatedly asking \u201cwhy\u201d \u2014 typically five times \u2014 until an "
                "underlying, fixable root cause is reached, rather than stopping at the first visible "
                "symptom. It originated at Toyota (credited to Sakichi Toyoda and popularized by Taiichi "
                "Ohno as part of the Toyota Production System) and is now widely used in Lean, Six Sigma, "
                "and general problem-solving."
            ),
            "when_to_use": (
                "Best suited to a single, moderately complex problem with a fairly linear cause-and-effect "
                "chain \u2014 for example, a recurring operational failure, a missed deadline, or a quality "
                "defect. It works well as a quick, low-cost first pass before deploying heavier tools. For "
                "problems with many interacting causes across different areas, it is often paired with a "
                "Fishbone diagram rather than used alone."
            ),
            "steps": [
                "State the problem clearly and specifically, with supporting evidence.",
                "Ask \u201cWhy did this happen?\u201d and record the answer, backed by data or direct observation where possible.",
                "Take that answer and ask \u201cwhy\u201d again, treating it as the new problem statement.",
                "Repeat for about five iterations, or until asking \u201cwhy\u201d stops producing new, useful information.",
                "Confirm the final answer is a systemic or process root cause \u2014 not a symptom, and not a person to blame.",
                "Agree on and implement a corrective action, then monitor whether it prevents the problem from recurring.",
            ],
            "example": (
                "Problem: A production line\u2019s fuse keeps blowing. Why #1: The machine overloaded, so the "
                "fuse blew. Why #2: The bearing lacked lubrication. Why #3: The lubrication pump wasn\u2019t "
                "circulating enough oil. Why #4: The pump\u2019s shaft was worn out. Why #5: No strainer was "
                "fitted, so metal shavings entered the system and wore the shaft down. Root cause: a missing "
                "strainer in the lubrication system. Corrective action: install a strainer and add it to the "
                "preventive maintenance checklist, rather than simply replacing the fuse each time it blows."
            ),
        },
        {
            "number": 2,
            "name": "Fishbone / Ishikawa Diagram",
            "definition": (
                "A visual brainstorming tool that maps every plausible cause of a problem into major "
                "categories branching off a central spine leading to the problem \u201chead,\u201d resembling a "
                "fish skeleton. Also called a cause-and-effect diagram, it was developed by Kaoru Ishikawa "
                "in 1943 and popularized through Toyota\u2019s quality circles in the 1960s."
            ),
            "when_to_use": (
                "Use when a problem likely has multiple, interacting causes across different areas (people, "
                "process, equipment, materials) rather than one obvious linear chain \u2014 for example, a "
                "persistent quality defect, a recurring customer-complaint pattern, or a process failure "
                "with no single clear explanation. It is often paired with 5 Whys to drill deeper into each "
                "branch once causes are mapped."
            ),
            "steps": [
                "Write the problem statement in a box at the \u201chead\u201d of the diagram.",
                "Draw a horizontal spine leading to it.",
                "Add major category branches \u2014 commonly the 6Ms: Manpower (People), Method, Machine, "
                "Material, Measurement, and Mother Nature (Environment) \u2014 or 4Ps for service contexts.",
                "With a cross-functional team, brainstorm specific possible causes under each category "
                "without judging or filtering them.",
                "Break broad causes into sub-causes by asking \u201cwhy\u201d within each branch.",
                "Review the completed diagram, identify the most likely causes, and verify them against data "
                "before acting.",
            ],
            "example": (
                "Problem: A bakery\u2019s bread batches are inconsistent in size. Manpower: new staff not "
                "trained on dough weighing. Method: no standard proofing time. Machine: oven temperature "
                "drifts by 15\u00b0F. Material: flour batches vary in protein content. Measurement: no scale "
                "calibration schedule. Environment: kitchen humidity swings seasonally. After mapping all "
                "branches, the team checks the data and finds oven temperature drift and untrained staff are "
                "the two most frequent contributors, so it schedules oven recalibration and creates a "
                "training checklist rather than addressing every branch at once."
            ),
        },
        {
            "number": 3,
            "name": "Pareto Analysis (80/20 Rule)",
            "definition": (
                "A prioritization technique based on the observation that roughly 80% of effects (such as "
                "complaints, defects, or revenue) come from about 20% of causes. It ranks causes by their "
                "contribution to a measured outcome so effort is concentrated on the \u201cvital few\u201d rather "
                "than spread evenly across the \u201ctrivial many.\u201d Named after economist Vilfredo Pareto, who "
                "observed that 80% of Italy\u2019s land was owned by 20% of its population."
            ),
            "when_to_use": (
                "Use when facing a long list of possible causes, problems, or items and needing to decide "
                "where to focus limited time or resources \u2014 for example, which product defects to fix "
                "first, which customers drive most revenue, or which complaint categories to address. It is "
                "less useful when causes contribute fairly evenly, since there is no dominant \u201cvital few\u201d "
                "to isolate."
            ),
            "steps": [
                "Identify and list the problems or causes to analyze.",
                "Choose a measurable unit (e.g., number of complaints, dollars lost, defect count).",
                "Collect data on each cause over a defined period.",
                "Rank causes from largest to smallest contribution.",
                "Calculate the cumulative percentage as causes are added, from largest to smallest.",
                "Plot as a bar chart of individual contributions with a cumulative percentage line, marking "
                "the 80% threshold to visually identify the vital few.",
                "Focus corrective action on the causes above that 80% cumulative threshold.",
            ],
            "example": (
                "A call center logs 500 complaints in a month across eight categories. Ranked by frequency: "
                "billing errors (210), late delivery (110), wrong item shipped (65), rude staff (40), "
                "website bugs (30), refund delays (25), packaging damage (15), other (5). Billing errors and "
                "late delivery alone account for 320 of 500 complaints (64%); adding wrong item shipped "
                "brings the cumulative total to 77%. The team concentrates next quarter\u2019s improvement "
                "budget on fixing billing and delivery-tracking issues rather than spreading effort across "
                "all eight categories."
            ),
        },
    ],
}

TIER2 = {
    "tier_label": "Tier 2",
    "tier_title": "Situational Analysis Frameworks",
    "tier_note": "Frameworks the AI uses to correctly understand business context before diagnosing.",
    "terms": [
        {
            "number": 4,
            "name": "SWOT Analysis",
            "definition": (
                "A structured framework for assessing an organization\u2019s internal Strengths and Weaknesses "
                "alongside external Opportunities and Threats, giving a snapshot of its current strategic "
                "position. Strengths and weaknesses are internal and controllable; opportunities and "
                "threats are external and largely outside the organization\u2019s control. The framework is "
                "commonly credited to Albert Humphrey\u2019s work at the Stanford Research Institute in the "
                "1960s\u201370s, though its exact origin is debated."
            ),
            "when_to_use": (
                "Use at the start of strategic planning, before entering a new market, launching a product, "
                "or setting annual goals \u2014 whenever a broad, high-level read of the current situation is "
                "needed before deeper analysis or decision-making. It is a starting diagnostic rather than a "
                "complete strategy on its own."
            ),
            "steps": [
                "Assemble a cross-functional team for varied perspectives.",
                "Brainstorm Strengths: internal advantages such as capabilities, resources, brand, or talent.",
                "Brainstorm Weaknesses: internal limitations, gaps, or vulnerabilities.",
                "Brainstorm Opportunities: favorable external trends or unmet needs in the market.",
                "Brainstorm Threats: external risks such as competitors, regulation, or disruption.",
                "Arrange findings into a 2\u00d72 matrix.",
                "Match strengths to opportunities, use strengths to offset threats, and note where weaknesses "
                "could block opportunities or amplify threats \u2014 then set priorities accordingly.",
            ],
            "example": (
                "A regional coffee chain is considering national expansion. Strengths: loyal local customer "
                "base, strong barista training program. Weaknesses: limited supply-chain infrastructure, "
                "thin marketing budget. Opportunities: growing demand for specialty coffee, availability of "
                "franchise capital. Threats: established national chains, rising bean prices. Resulting "
                "strategy: leverage the strong training program (strength) to support a franchise model "
                "(opportunity), while first investing in supply-chain capacity (weakness) before scaling, to "
                "avoid overextending against larger competitors (threat)."
            ),
        },
        {
            "number": 5,
            "name": "PESTLE Analysis",
            "definition": (
                "A framework for scanning the macro-environmental factors \u2014 Political, Economic, Social, "
                "Technological, Legal, and Environmental \u2014 that can affect an organization from outside, "
                "independent of its internal capabilities. It is often used to feed the \u201cOpportunities\u201d "
                "and \u201cThreats\u201d sides of a SWOT analysis. The same framework is sometimes ordered as "
                "PESTEL; the naming difference does not change its content."
            ),
            "when_to_use": (
                "Use when entering a new market or country, before major long-term investment decisions, or "
                "periodically as part of strategic planning to spot external shifts \u2014 regulatory changes, "
                "economic cycles, technology disruption \u2014 before they affect performance. It is most "
                "valuable for organizations sensitive to macroeconomic or regulatory conditions."
            ),
            "steps": [
                "Define the market, country, or industry scope of the analysis.",
                "Political: assess government stability, trade policy, taxation, and regulation.",
                "Economic: assess growth, inflation, interest and exchange rates, and unemployment.",
                "Social: assess demographics, lifestyle trends, and cultural attitudes.",
                "Technological: assess innovation pace, automation, and R&D activity.",
                "Legal: assess employment law, consumer protection, and industry-specific regulation.",
                "Environmental: assess sustainability requirements, climate impact, and resource availability.",
                "Rank which factors matter most for the specific decision and feed them into strategic "
                "planning or a SWOT analysis.",
            ],
            "example": (
                "An EV manufacturer is evaluating entry into a new country. Political: government EV "
                "subsidies (favorable). Economic: rising middle-class income (favorable) but currency "
                "volatility (risk). Social: growing environmental awareness among younger buyers (favorable). "
                "Technological: limited charging infrastructure (unfavorable). Legal: new emissions standards "
                "taking effect in two years (favorable timing). Environmental: government targets to cut "
                "transport emissions 30% by 2030 (favorable). Conclusion: political and environmental "
                "tailwinds support entry, but the company should pair its launch with investment in charging "
                "infrastructure to offset the technological gap."
            ),
        },
        {
            "number": 6,
            "name": "Porter\u2019s Five Forces",
            "definition": (
                "A framework for analyzing the competitive intensity and profit potential of an industry "
                "through five structural forces: competitive rivalry, threat of new entrants, threat of "
                "substitutes, bargaining power of suppliers, and bargaining power of buyers. Developed by "
                "Michael Porter (Harvard Business School, 1979), it analyzes the structure of an industry "
                "rather than a single company\u2019s internal strategy."
            ),
            "when_to_use": (
                "Use when assessing whether to enter, exit, or invest further in an industry, or when trying "
                "to understand why an industry\u2019s average profitability is structurally high or low. It "
                "complements internally focused tools like SWOT by explaining external competitive pressure."
            ),
            "steps": [
                "Define the industry and its boundaries clearly.",
                "Assess competitive rivalry: number of competitors, industry growth rate, product "
                "differentiation.",
                "Assess threat of new entrants: barriers to entry such as capital requirements, regulation, "
                "and brand loyalty.",
                "Assess threat of substitutes: availability of alternative products or services meeting the "
                "same need.",
                "Assess supplier bargaining power: supplier concentration, switching costs, availability of "
                "inputs.",
                "Assess buyer bargaining power: buyer concentration, price sensitivity, ease of switching.",
                "Synthesize the five ratings into an overall view of industry attractiveness and where a "
                "company\u2019s negotiating leverage is weakest.",
            ],
            "example": (
                "Analyzing the commercial airline industry: Rivalry \u2014 high (many carriers competing on "
                "price over the same routes). New entrants \u2014 low threat (high capital costs, regulatory "
                "approval, limited gate access). Substitutes \u2014 moderate (high-speed rail on short routes, "
                "video conferencing for business travel). Supplier power \u2014 high (only two major aircraft "
                "manufacturers, powerful pilot unions, few fuel suppliers). Buyer power \u2014 high "
                "(price-comparison sites make switching easy). Conclusion: high rivalry combined with high "
                "supplier and buyer power explains the industry\u2019s historically thin profit margins, and a "
                "new entrant would need a clear cost or niche advantage to survive."
            ),
        },
    ],
}

TIER3 = {
    "tier_label": "Tier 3",
    "tier_title": "Decision Frameworks",
    "tier_note": "Frameworks used at the end of the process to shape the final recommendation.",
    "terms": [
        {
            "number": 7,
            "name": "Impact-Effort Matrix (Prioritization Matrix)",
            "definition": (
                "A simple 2\u00d72 grid used to prioritize tasks, ideas, or initiatives by plotting their "
                "expected impact (value or benefit) against the effort (time, cost, resources) required to "
                "implement them. This produces four quadrants: Quick Wins (high impact, low effort), Major "
                "Projects (high impact, high effort), Fill-Ins (low impact, low effort), and Thankless Tasks "
                "or Hard Slogs (low impact, high effort). Also called an action priority matrix."
            ),
            "when_to_use": (
                "Use when facing a long backlog of competing ideas, projects, or improvement initiatives and "
                "needing a fast, visual way to decide what to tackle first. It is common in product "
                "management, project planning, and as a follow-up step after a Fishbone or Pareto analysis "
                "has surfaced candidate actions."
            ),
            "steps": [
                "List all candidate tasks or initiatives.",
                "Define consistent scoring criteria for \u201cimpact\u201d (e.g., revenue, satisfaction, risk "
                "reduction) and \u201ceffort\u201d (e.g., time, cost, people needed).",
                "Score each item on both dimensions, either numerically or as high/medium/low.",
                "Plot each item on the grid, with effort on the x-axis and impact on the y-axis.",
                "Identify which quadrant each item falls into.",
                "Sequence work: start with Quick Wins, plan Major Projects, fit in Fill-Ins opportunistically, "
                "and deprioritize or eliminate Thankless Tasks.",
                "Revisit the matrix periodically as effort estimates and priorities shift.",
            ],
            "example": (
                "A software team has five backlog items after a user survey. Fixing a login bug: high "
                "impact, low effort \u2192 Quick Win, done this sprint. Rebuilding the onboarding flow: high "
                "impact, high effort \u2192 Major Project, scheduled for next quarter. Adding a dark-mode "
                "toggle: low impact, low effort \u2192 Fill-In, done when time allows. Migrating to a new "
                "database: low impact to users but high effort \u2192 deprioritized for now. Redesigning the "
                "settings page: medium impact, medium effort \u2192 placed on the roadmap after the Quick Win "
                "and before the Major Project."
            ),
        },
        {
            "number": 8,
            "name": "Decision Tree Analysis",
            "definition": (
                "A visual, flowchart-style tool for evaluating decisions made under uncertainty by mapping "
                "decision points (squares), chance events with assigned probabilities (circles), and final "
                "outcomes or payoffs (end nodes), then calculating the expected value of each path to "
                "identify the option with the best expected return."
            ),
            "when_to_use": (
                "Use for decisions with a small number of discrete options, each followed by uncertain "
                "outcomes with estimable probabilities and payoffs \u2014 for example, whether to launch a new "
                "product, invest in a project, or settle versus litigate. It is less suited to decisions "
                "involving continuous variables or highly unpredictable, unquantifiable risk."
            ),
            "steps": [
                "Define the decision to be made and draw a decision node (square) as the starting point.",
                "Add branches for each available option.",
                "After branches involving uncertainty, add a chance node (circle) with branches for each "
                "possible outcome.",
                "Assign a probability to each branch from a chance node (probabilities from one node must "
                "sum to 1).",
                "Assign a payoff (financial or other value) at each end node.",
                "Calculate the expected value of each chance node by multiplying each outcome\u2019s payoff by "
                "its probability and summing them.",
                "Work backward, right to left, through the tree, choosing at each decision node the branch "
                "with the highest expected value.",
            ],
            "example": (
                "A company is deciding whether to launch a new product. Decision node: Launch vs. Don\u2019t "
                "Launch. If Launch, a chance node follows: 60% chance of market success (payoff $500,000) and "
                "40% chance of failure (payoff \u2212$150,000). Expected value of launching = (0.6 \u00d7 $500,000) "
                "+ (0.4 \u00d7 \u2212$150,000) = $300,000 \u2212 $60,000 = $240,000. Don\u2019t Launch has a payoff of $0. "
                "Since $240,000 is greater than $0, the decision tree recommends launching \u2014 provided the "
                "company can tolerate the 40% chance of a $150,000 loss."
            ),
        },
    ],
}

TIER4 = {
    "tier_label": "Tier 4",
    "tier_title": "Core Financial & Business Vocabulary",
    "tier_note": "Not frameworks \u2014 terms the AI needs to correctly read and reason about business data in cases.",
    "terms": [
        {
            "number": 9,
            "name": "Profitability",
            "definition": (
                "A measure of how much financial gain a business generates relative to its revenue, assets, "
                "or investment, after accounting for costs. At its simplest, profit equals revenue minus "
                "costs; costs are typically split into cost of goods sold (COGS) \u2014 the direct costs of "
                "producing what is sold \u2014 and operating expenses (overhead such as rent, salaries, "
                "marketing), plus non-operating items like interest and taxes."
            ),
            "when_to_use": (
                "Use whenever assessing whether a business, product line, or business unit is financially "
                "sustainable \u2014 for pricing decisions, evaluating whether to continue or discontinue a "
                "product, comparing performance across periods, or communicating financial health to "
                "investors or lenders."
            ),
            "steps": [
                "Determine total revenue for the period.",
                "Subtract Cost of Goods Sold (COGS) to get Gross Profit.",
                "Subtract operating expenses (rent, salaries, marketing, admin) to get Operating Profit "
                "(EBIT).",
                "Subtract interest and taxes to get Net Profit \u2014 the \u201cbottom line.\u201d",
                "Express each profit level as a percentage of revenue (margin) to compare across periods or "
                "against competitors of different sizes.",
                "Track trends over multiple periods rather than relying on a single snapshot.",
            ],
            "example": (
                "A small furniture maker has quarterly revenue of $200,000. COGS (wood, hardware, direct "
                "labor) is $110,000, giving a Gross Profit of $90,000 (45% gross margin). Operating expenses "
                "(rent, admin salaries, marketing) total $50,000, giving an Operating Profit of $40,000. "
                "Interest on a business loan is $5,000 and taxes are $8,000, leaving a Net Profit of $27,000 "
                "(13.5% net margin). The business is profitable at every level, but the gap between the 45% "
                "gross margin and 13.5% net margin shows that overhead and financing costs are consuming a "
                "large share of the money left after production costs."
            ),
        },
        {
            "number": 10,
            "name": "Gross Margin vs. Net Margin",
            "definition": (
                "Both are profitability ratios expressed as a percentage of revenue. Gross Margin = "
                "(Revenue \u2212 COGS) / Revenue \u00d7 100, measuring how efficiently a company produces its goods "
                "or services before overhead. Net Margin = Net Profit / Revenue \u00d7 100, measuring what share "
                "of every revenue dollar remains as profit after all costs, including operating expenses, "
                "interest, and taxes."
            ),
            "when_to_use": (
                "Use gross margin to evaluate production and pricing efficiency, and to compare cost "
                "structures across periods or similar companies. Use net margin to evaluate overall "
                "profitability and financial health, since it captures the full cost picture. Comparing the "
                "gap between the two reveals how much operating and non-operating costs are eating into "
                "profit."
            ),
            "steps": [
                "Gather revenue and COGS for the period.",
                "Calculate Gross Profit = Revenue \u2212 COGS.",
                "Calculate Gross Margin = Gross Profit / Revenue \u00d7 100.",
                "Gather all remaining expenses: operating costs, interest, and taxes.",
                "Calculate Net Profit = Gross Profit \u2212 remaining expenses.",
                "Calculate Net Margin = Net Profit / Revenue \u00d7 100.",
                "Compare the two margins over time or against industry benchmarks to spot cost-control "
                "issues.",
            ],
            "example": (
                "A clothing retailer reports $1,000,000 in revenue and $600,000 in COGS. Gross Profit = "
                "$400,000, so Gross Margin = 40%. After deducting $250,000 in operating expenses, $20,000 in "
                "interest, and $30,000 in taxes, Net Profit = $100,000, so Net Margin = 10%. The 30-point gap "
                "between the 40% gross margin and 10% net margin signals that overhead, interest, and taxes "
                "\u2014 not production costs \u2014 are the biggest drag on the retailer\u2019s bottom line, pointing "
                "management toward cutting operating costs rather than renegotiating supplier prices."
            ),
        },
        {
            "number": 11,
            "name": "Market Share",
            "definition": (
                "The percentage of total sales (by revenue or units) within a defined market that is "
                "captured by a specific company, calculated as Market Share = (Company Sales / Total Market "
                "Sales) \u00d7 100. It can be measured by revenue or by unit volume, and for the total market or "
                "a specific customer segment."
            ),
            "when_to_use": (
                "Use to gauge a company\u2019s competitive position relative to rivals, to track whether growth "
                "is outpacing or lagging the overall market, and to support decisions about marketing "
                "investment, pricing strategy, or expansion. It is most meaningful when compared over time "
                "or against named competitors, since a single figure in isolation says little."
            ),
            "steps": [
                "Define the relevant market: product category, geography, customer segment, and time period.",
                "Gather the company\u2019s sales revenue or unit volume for that period.",
                "Gather or estimate total market sales for the same period, using industry reports, market "
                "research, or public competitor filings.",
                "Divide company sales by total market sales and multiply by 100.",
                "Repeat for prior periods to see whether share is growing, shrinking, or stable.",
                "Compare against named competitors, where data allows, to identify the market leader and "
                "relative position.",
            ],
            "example": (
                "A regional soft-drink brand sells $12 million worth of product in a metro area where total "
                "soft-drink sales are $80 million for the year. Market Share = ($12M / $80M) \u00d7 100 = 15%. "
                "The prior year the brand\u2019s share was 12%, so management concludes the brand is gaining "
                "ground even though total category sales barely changed \u2014 evidence that growth is coming "
                "from taking share away from competitors rather than from overall market expansion."
            ),
        },
        {
            "number": 12,
            "name": "ROI (Return on Investment)",
            "definition": (
                "A profitability ratio that measures the financial return generated by an investment "
                "relative to its cost, calculated as ROI = (Net Profit / Cost of Investment) \u00d7 100, where "
                "Net Profit = Gain from Investment \u2212 Cost of Investment. It is expressed as a percentage; "
                "a positive ROI means the investment generated more value than it cost."
            ),
            "when_to_use": (
                "Use when comparing the relative attractiveness of two or more investments or initiatives "
                "(marketing campaigns, equipment purchases, projects), when justifying a spending decision to "
                "stakeholders, or when reviewing whether a past investment paid off. It is best used alongside "
                "other metrics such as payback period or timeframe, since ROI alone does not capture how long "
                "it took to earn the return."
            ),
            "steps": [
                "Identify the total cost of the investment, including all associated spend.",
                "Identify the total gain or return generated by the investment over the measurement period.",
                "Calculate Net Profit = Gain from Investment \u2212 Cost of Investment.",
                "Calculate ROI = (Net Profit / Cost of Investment) \u00d7 100.",
                "Compare the ROI figure against alternative uses of the same funds, or against a target or "
                "benchmark return.",
                "Note the time period involved, since a 30% ROI over one year is very different from 30% "
                "over five years.",
            ],
            "example": (
                "A company spends $10,000 on a marketing campaign, which generates $13,000 in additional "
                "sales attributable to that campaign. Net Profit = $13,000 \u2212 $10,000 = $3,000. ROI = "
                "($3,000 / $10,000) \u00d7 100 = 30%. A competing initiative \u2014 upgrading equipment for $50,000 "
                "\u2014 is expected to save $20,000 per year in costs, an ROI of 40% in year one. The equipment "
                "upgrade shows a higher percentage return, though the marketing campaign requires a much "
                "smaller upfront cash outlay, which the company must also weigh in its decision."
            ),
        },
        {
            "number": 13,
            "name": "Break-even Point",
            "definition": (
                "The level of sales, in units or revenue, at which total revenue exactly equals total costs, "
                "meaning the business is neither making a profit nor a loss. In units, it is calculated as "
                "Break-even Point = Fixed Costs / (Price per Unit \u2212 Variable Cost per Unit)."
            ),
            "when_to_use": (
                "Use when launching a new product, setting prices, or deciding whether a business venture is "
                "viable, to determine the minimum sales volume needed to cover costs before evaluating "
                "assumptions about actual demand. It is also useful for stress-testing pricing changes or "
                "cost increases."
            ),
            "steps": [
                "Identify total fixed costs for the period \u2014 costs that don\u2019t change with production "
                "volume, such as rent and salaries.",
                "Identify the variable cost per unit \u2014 costs that scale with each unit produced, such as "
                "materials and direct labor.",
                "Identify the selling price per unit.",
                "Calculate the contribution margin per unit = Price per Unit \u2212 Variable Cost per Unit.",
                "Calculate Break-even Point (units) = Fixed Costs / Contribution Margin per Unit.",
                "Multiply by price to get the break-even point in revenue, if needed.",
                "Compare the break-even volume against realistic demand forecasts to judge feasibility.",
            ],
            "example": (
                "A startup plans to manufacture a new gadget with fixed costs (rent, salaries, equipment "
                "lease) of $20,000 per month. Each unit costs $5 in materials and labor to produce and sells "
                "for $15. Contribution margin = $15 \u2212 $5 = $10 per unit. Break-even Point = $20,000 / $10 = "
                "2,000 units per month. If the company forecasts demand of only 1,200 units in its first "
                "month, it will operate at a loss until sales volume grows, so it may need to raise the "
                "price, cut fixed costs, or secure additional runway to survive the ramp-up period."
            ),
        },
        {
            "number": 14,
            "name": "CAGR (Compound Annual Growth Rate)",
            "definition": (
                "A single, smoothed growth rate describing how much a value \u2014 revenue, investment, "
                "customer base \u2014 would have had to grow each year, compounding annually, to go from its "
                "starting value to its ending value over a given number of years, even though actual "
                "year-to-year growth was likely uneven. Formula: CAGR = (Ending Value / Beginning Value)"
                "^(1/n) \u2212 1, where n is the number of years."
            ),
            "when_to_use": (
                "Use to compare long-term growth trends across companies, products, or investments of "
                "different sizes and timeframes, or to communicate a company\u2019s growth trajectory to "
                "investors without the noise of quarter-to-quarter volatility. It is not suitable for "
                "describing performance in any single interim year, since it hides volatility within the "
                "period."
            ),
            "steps": [
                "Identify the Beginning Value (starting figure) and the Ending Value (final figure).",
                "Determine the number of years (n) between the two values.",
                "Divide Ending Value by Beginning Value.",
                "Raise that result to the power of (1/n).",
                "Subtract 1 from the result.",
                "Multiply by 100 to express the result as a percentage.",
                "Interpret the result as the constant annual growth rate that would produce the same "
                "overall change.",
            ],
            "example": (
                "A company\u2019s annual revenue grew from $2 million to $4.5 million over 5 years. CAGR = "
                "(4,500,000 / 2,000,000)^(1/5) \u2212 1 = (2.25)^(0.2) \u2212 1 \u2248 1.1756 \u2212 1 = 0.1756, or about "
                "17.6%. Even though actual annual growth may have been 30% one year and 5% another, the "
                "CAGR tells stakeholders that, on average, revenue grew at a steady compounded rate of "
                "roughly 17.6% per year \u2014 useful for comparing against a competitor whose revenue grew from "
                "$1 million to $2 million over the same 5 years, a lower CAGR of about 14.9%."
            ),
        },
        {
            "number": 15,
            "name": "KPI (Key Performance Indicator)",
            "definition": (
                "A specific, measurable value used to track progress toward a defined business objective. "
                "Unlike a general metric, which simply measures an activity, a KPI is deliberately selected "
                "because it reflects something strategically important \u2014 such as revenue growth, customer "
                "churn, or on-time delivery rate \u2014 and is typically defined using SMART criteria: Specific, "
                "Measurable, Achievable, Relevant, and Time-bound."
            ),
            "when_to_use": (
                "Use when setting up performance dashboards, tracking progress against strategic goals, or "
                "reading business case data \u2014 any time it is necessary to judge objectively whether \u201cthe "
                "business is on track\u201d rather than anecdotally. A small set of well-chosen KPIs, rather than "
                "dozens of raw metrics, keeps decision-makers focused on what actually matters."
            ),
            "steps": [
                "Identify the specific business objective the KPI should support (e.g., \u201cincrease customer "
                "retention\u201d).",
                "Choose a measurable indicator directly tied to that objective (e.g., \u201cmonthly customer "
                "churn rate\u201d).",
                "Set a target and time frame (e.g., \u201creduce churn from 5% to 3% within two quarters\u201d).",
                "Confirm the KPI is achievable and realistically influenced by the team tracking it.",
                "Establish a reliable, repeatable way to measure and report it: data source, frequency, and "
                "owner.",
                "Review the KPI regularly against its target and adjust strategy or tactics if it drifts off "
                "track.",
            ],
            "example": (
                "A SaaS company sets the strategic goal of improving customer retention. It selects "
                "\u201cMonthly Churn Rate\u201d as its KPI, defined as (customers lost in the month / customers at "
                "start of month) \u00d7 100, with a target of reducing churn from 5% to 3% within two quarters. "
                "Each month, the customer success team reports actual churn on a shared dashboard. In month "
                "one, churn is 4.6%; by month four, it reaches 3.1% after the team introduces a proactive "
                "onboarding program \u2014 showing the KPI is trending toward its target and validating that the "
                "onboarding initiative is working."
            ),
        },
    ],
}

ALL_TIERS = [TIER1, TIER2, TIER3, TIER4]