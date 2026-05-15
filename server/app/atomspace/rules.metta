; ---------------------------------------------------------------------------
; Step 1: AtomSpace / Constitutional Knowledge Graph
; ---------------------------------------------------------------------------
; This file is the source of truth. Python is only the execution bridge that
; traverses these atoms and enforces the symbolic laws before tools can run.

; ===== 1.0- Autonomous actors, users, and teams =============================
(subject atnatewos manager)
(subject coach_joe coach)
(subject dr_smith staff)
(subject guest_user observer)
(subject blinders_ai staff)
(controls_team atnatewos blinders_elite_fc)
(delegated_agent atnatewos blinders_ai)

(team blinders_elite_fc)
(team_owner blinders_elite_fc atnatewos)

; ===== 1.1 Recursive role hierarchy ===========================================
(isA manager coach)
(isA coach staff)
(isA staff observer)

; ===== 1.2 Permission model =================================================
(permission observer view_team)
(permission staff update_player_status)
(permission staff view_risk_report)
(permission coach set_captain) 
(permission coach view_risk_report)
(permission manager view_risk_report)
(permission manager transfer_player)

(deny_permission observer rewrite_constitution)

; ===== 1.3 Runtime context ==================================================
(context gameweek_deadline_open true)
(context cup_mode active)
(context gameweek_final false)
(context transfer_window_open true)

; ===== 1.4 League constraints ===============================================
(constraint max_squad_size 15)
(constraint max_players_per_club 3)
(constraint min_goalkeepers 2)
(constraint max_free_transfer_bank 5)
(constraint free_transfer_allowance blinders_elite_fc 1)
(constraint points_penalty_per_extra_transfer 4)
(constraint hard_transfer_cap_without_chip 3)
(constraint review_required_risk high)


; ===== 1.5 Constitutional law registry =====================================
(law L1 role_authority "Only inherited constitutional permissions can authorize actions.")
(law L2 deadline_gate "Transfers and captaincy changes require an open gameweek deadline.")
(law L3 club_quota "A fantasy squad may contain at most three players from one real club.")
(law L4 budget_integrity "The team bank cannot become negative after transfers.")
(law L5 captain_health "An injured or suspended player cannot be captain.")
(law L6 transfer_limit "Non-chip transfer plans cannot exceed the hard transfer cap.")
(law L8 chip_availability "A chip can only be used when available to the team.")
(law L10 reviewer_audit "High-risk actions require reviewer audit logging.")

; ===== 2.0 Team state ===========================================================
(bank blinders_elite_fc 0.0)

; --- 15 Player Squad (Valid FPL Rules: Max 3 per club) ---
(squad blinders_elite_fc Martinez)      ; AVL (1)
(squad blinders_elite_fc Pickford)      ; EVE (1)
(squad blinders_elite_fc Saliba)        ; ARS (1)
(squad blinders_elite_fc Gabriel)       ; ARS (2)
(squad blinders_elite_fc Gvardiol)      ; MCI (1)
(squad blinders_elite_fc AlexanderArnold) ; LIV (1)
(squad blinders_elite_fc Burn)          ; NEW (1)
(squad blinders_elite_fc Saka)          ; ARS (3)
(squad blinders_elite_fc Foden)         ; MCI (2)
(squad blinders_elite_fc Salah)         ; LIV (2)
(squad blinders_elite_fc Palmer)        ; CHE (1)
(squad blinders_elite_fc Gordon)        ; NEW (2)
(squad blinders_elite_fc Haaland)       ; MCI (3)
(squad blinders_elite_fc Watkins)       ; AVL (2)
(squad blinders_elite_fc Isak)          ; NEW (3)

; ===== 2.1 Player registry ======================================================
; --- Goalkeepers ---
(player Martinez AstonVilla goalkeeper 5.0 fit goalkeeper)
(player Pickford Everton goalkeeper 4.8 fit goalkeeper)
(player Saliba Arsenal defender 6.0 fit defender)
(player Gabriel Arsenal defender 5.4 fit defender)
(player White Arsenal defender 6.1 fit defender)
(player Saka Arsenal midfielder 9.1 fit star_player)
(player Odegaard Arsenal midfielder 8.5 fit star_player)
(player Foden ManCity midfielder 9.4 fit star_player)
(player Salah Liverpool midfielder 13.5 fit star_player)
(player Palmer Chelsea midfielder 10.5 fit star_player)
(player Haaland ManCity forward 14.3 fit star_player)
(player Watkins AstonVilla forward 9.0 fit finisher)
(player Isak Newcastle forward 8.4 fit finisher)
(player Havertz Arsenal forward 7.5 fit finisher)

; ===== 2.2 Recursive player class graph ========================================
(isA star_player captain_candidate)
(isA finisher captain_candidate)

; ===== 3.0 Action requirements ==================================================
(requires_permission transfer_player transfer_player)
(requires_permission set_captain set_captain)

(requires_context transfer_player gameweek_deadline_open true L2)
(requires_context transfer_player transfer_window_open true L2)
(requires_context set_captain gameweek_deadline_open true L2)

(action_constraint transfer_player max_squad_size L1)
(action_constraint transfer_player max_players_per_club L3)
(action_constraint transfer_player budget_non_negative L4)
(action_constraint transfer_player transfer_cap L6)
(action_constraint set_captain captain_must_be_in_squad L5)
(action_constraint set_captain captain_must_be_fit L5)
(action_constraint set_captain captain_class_candidate L5)

(risk transfer_player multi_transfer medium)
