from scipy.stats import norm

def get_luck_percentile(avg_pulls, win_rate, pool_type="weapon"):
    if pool_type == "weapon":
        # 根據您的要求：武器池期望值 105.7
        # 參數設定：平均抽數 μ=53.3, σ=10.5; 勝率 μ=0.504, σ=0.15
        p_mu, p_sigma = 53.3, 10.5
        w_mu, w_sigma = 0.504, 0.15
    else:
        # 限定角色池參數
        p_mu, p_sigma = 62.3, 12
        w_mu, w_sigma = 0.55, 0.15

    # 計算抽數百分位 (越低越好，所以用 1 - cdf)
    pull_score = 1 - norm.cdf(avg_pulls, p_mu, p_sigma)
    # 計算勝率百分位 (越高越好)
    win_score = norm.cdf(win_rate, w_mu, w_sigma)
    
    # 回傳綜合百分比
    return (pull_score + win_score) / 2

def get_rank_name(score):
    if score > 0.95: return "終極無敵至尊大歐皇"
    if score > 0.85: return "大歐皇"
    if score > 0.70: return "小歐皇"
    if score > 0.55: return "小幸運"
    if score > 0.45: return "氣運平平"
    if score > 0.30: return "轉運中(小非)"
    if score > 0.20: return "霉運纏身(小非)"
    if score > 0.05: return "大非酋"
    return "終極無敵至尊非酋王"