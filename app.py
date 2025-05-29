from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages

# Policy options and their values
ESC_POLICY_OPTIONS = {
    "150000": {"coverage": 150000, "premium": 12272},
    "200000": {"coverage": 200000, "premium": 14160},
    "300000": {"coverage": 300000, "premium": 16048},
    "500000": {"coverage": 500000, "premium": 19352},
    "700000": {"coverage": 700000, "premium": 24072},
    "1000000": {"coverage": 1000000, "premium": 31624},
    "1500000": {"coverage": 1500000, "premium": 40120}
}

PARENT_POLICY_OPTIONS = {
    "300000": {"coverage": 300000, "premium": 18585},
    "500000": {"coverage": 500000, "premium": 23305},
    "800000": {"coverage": 800000, "premium": 30385},
    "1000000": {"coverage": 1000000, "premium": 33040},
    "1500000": {"coverage": 1500000, "premium": 46905}
}

TOPUP_POLICY_OPTIONS = {
    "100000": {"coverage": 100000, "premium": 8850},
    "200000": {"coverage": 200000, "premium": 11800},
    "300000": {"coverage": 300000, "premium": 14750},
    "400000": {"coverage": 400000, "premium": 17700},
    "500000": {"coverage": 500000, "premium": 20650},
    "750000": {"coverage": 750000, "premium": 29500},
    "1000000": {"coverage": 1000000, "premium": 35400}
}

# Parent coverage options
PARENT_COVERAGE_OPTIONS = {
    "father": "Father / Father-in-Law",
    "mother": "Mother / Mother-in-Law",
    "both": "Father / Father-in-Law & Mother / Mother-in-Law"
}

@app.route('/')
def home():
    return render_template('index.html', 
                          esc_options=ESC_POLICY_OPTIONS,
                          parent_options=PARENT_POLICY_OPTIONS,
                          topup_options=TOPUP_POLICY_OPTIONS,
                          parent_coverage_options=PARENT_COVERAGE_OPTIONS)

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        # Get form data
        esc_policy = request.form.get('esc_policy')
        parent_policy = request.form.get('parent_policy')
        parent_coverage = request.form.get('parent_coverage')
        topup_policy = request.form.get('topup_policy')
        
        # Validate ESC policy is selected (mandatory)
        if not esc_policy:
            flash('ESC Policy selection is mandatory', 'error')
            return redirect(url_for('home'))
            
        # If parent policy is selected but no coverage option is chosen, default to "father"
        if parent_policy and not parent_coverage:
            parent_coverage = "father"
        
        # Calculate totals
        total_coverage = 0
        subtotal_premium = 0
        
        # Process ESC policy selection
        esc_coverage = 0
        esc_premium = 0
        if esc_policy in ESC_POLICY_OPTIONS:
            esc_coverage = ESC_POLICY_OPTIONS[esc_policy]["coverage"]
            esc_premium = ESC_POLICY_OPTIONS[esc_policy]["premium"]
            total_coverage += esc_coverage
            subtotal_premium += esc_premium
        
        # Process Parent policy selection
        parent_coverage_value = 0
        parent_premium = 0
        parent_coverage_type = ""
        if parent_policy and parent_policy in PARENT_POLICY_OPTIONS and parent_coverage:
            parent_coverage_value = PARENT_POLICY_OPTIONS[parent_policy]["coverage"]
            parent_premium = PARENT_POLICY_OPTIONS[parent_policy]["premium"]
            parent_coverage_type = PARENT_COVERAGE_OPTIONS.get(parent_coverage, "")
            
            # Apply multiplier based on coverage type
            if parent_coverage == "both":
                # For both parents, multiply premium by 2
                parent_premium = parent_premium * 2
            elif parent_coverage == "father" or parent_coverage == "mother":
                # For single parent, keep as is (multiply by 1)
                parent_premium = parent_premium * 1
            
            total_coverage += parent_coverage_value
            subtotal_premium += parent_premium
        
        # Process Top-up policy selection
        topup_coverage = 0
        topup_premium = 0
        if topup_policy and topup_policy in TOPUP_POLICY_OPTIONS:
            topup_coverage = TOPUP_POLICY_OPTIONS[topup_policy]["coverage"]
            topup_premium = TOPUP_POLICY_OPTIONS[topup_policy]["premium"]
            total_coverage += topup_coverage
            subtotal_premium += topup_premium
        
        # Fixed CTC contribution
        ctc_contribution = 10000
        
        # Calculate final premium after CTC contribution
        total_premium = max(0, subtotal_premium - ctc_contribution)
        
        # Calculate monthly share (total premium divided by 10) and round up
        import math
        monthly_share = math.ceil(total_premium / 10)
        
        # Prepare selections for display
        selections = {
            'ESC Policy': {
                'option': esc_policy,
                'coverage': esc_coverage,
                'premium': esc_premium
            },
            'Parent Policy': {
                'option': parent_policy,
                'coverage': parent_coverage_value,
                'premium': parent_premium,
                'coverage_type': parent_coverage_type
            },
            'Top-Up Policy': {
                'option': topup_policy,
                'coverage': topup_coverage,
                'premium': topup_premium
            },
            'Subtotal': {
                'premium': subtotal_premium
            },
            'From CTC': {
                'premium': ctc_contribution
            },
            'Total': {
                'coverage': total_coverage,
                'premium': total_premium,
                'monthly_share': monthly_share
            }
        }
        
        return render_template('result.html', selections=selections)
    
    # If not POST, redirect to home
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)