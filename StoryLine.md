### Title Proposal

**"A Dynamical Regime Shift Limits the Capacity for Abstract Sequence Compression in Primate Auditory Cortex"**
*(Rationale: "Regime Shift" accurately describes the PCA trajectory divergence found in Figure 3, avoiding the potential overstatement of "Collapse" while maintaining strong physical framing.)*

---

### Abstract Concept:

* **Context:** Primate brains must compress sensory information, but the biological limits of this compression are unknown.

* **Observation:** We recorded ECoG in macaques processing sequences of varying Complexity and Length.

* **Result 1 (Sensitivity):** In the short regime, auditory cortex tracks structural complexity (MDL), albeit through diverse individual strategies (efficiency vs. recruitment).

* **Result 2 (The Functional Breakdown):** Crucially, regardless of the encoding strategy, a universal capacity limit emerged. As sequence length exceeded working memory capacity, the neural representation of complexity collapsed.

* **Result 3 (The Mechanism - The Hook):** This was not simple fatigue. State-space analysis reveals a "Dynamical Regime Shift," where neural trajectories escape the computational manifold into a disjoint state space.

* **Conclusion:** We identify the dynamical signature of cognitive overload. The primate auditory cortex possesses the machinery for compression but is constrained by a rigid state-space boundary, distinguishing it from the open-ended generative capacity of humans.

---

### Introduction: The Biological Constraints of the "Language of Thought"

* **Theoretical Framework:** The "Language of Thought" hypothesis posits that brains compress sequences using generative rules (MDL) rather than transition probabilities. While humans nest these rules recursively, the phylogenetic boundaries of this ability are unknown.
* **The Reframed Problem:** It is not merely a question of *software* (do monkeys have the rule?) but of *State-Space Stability* (can they sustain the rule?). We hypothesize that the neural workspace for sequence compression is bounded by a "Dynamical Capacity Limit."
* **The Investigation:** We challenge the macaque auditory cortex with a "Stress Test" paradigm—varying both **Complexity (MDL)** and **Length**. This dissociates specific compression strategies from the universal dynamical limits of the system.

---

### Results Section 1: Diverse Strategies for Compression (The Computational Manifold)

*Logic: Demonstrate that despite individual variability, the auditory cortex is sensitive to structural complexity in the low-load regime.*

* **Diverse Encoding Strategies:**
    * In the "Short" regime (4–8 items), neural activity significantly tracks MDL complexity, but the *mode* of implementation varies by subject.
    * **Subject Boss ("Efficiency"):** Exhibits a negative slope (-2.05), where simpler sequences (Low MDL) elicit larger prediction error signals (MMN-proxy), consistent with a "Predictive Coding" model.
    * **Subject Carol ("Recruitment"):** Exhibits a positive slope (+2.00), where complex sequences (High MDL) drive higher aggregate neural engagement (AUC), consistent with a "Cognitive Effort" model.
    * *Synthesized Takeaway:* Validating the "Language of Thought" in non-humans requires looking beyond a single canonical response. The auditory cortex *is* compressing information, utilizing subject-specific strategies to represent structure.

* **Supplementary Evidence (Sensitivity to Rule):**
    * Exploratory frequency tagging (ITC) corroborates this sensitivity. We observe condition-specific phase-locking to abstract rules (e.g., 2Hz alternation) in short sequences (e.g., Carol, Length 6, p < 0.05). While not globally robust, this supports the view that the machinery for abstract structure tracking is present but fragile.

---

### Results Section 2: The Universal Collapse (The Capacity Limit)

*Logic: Show that regardless of the strategy (Efficiency or Recruitment), the system hits the same dynamical wall.*

* **The Gating Phenomenon:**
    * We traced the fidelity of these encoding strategies as Sequence Length increased from 8 to 16 items.
    * **The Crash:**
        * **Boss:** The efficient error-signaling mechanism breaks down. The slope flips from -2.05 to +1.17 (p ~ 0.05), indicating a loss of precision.
        * **Carol:** The recruitment mechanism collapses. The positive encoding of complexity vanishes (AUC slope drops to noise levels).
* *Key Insight:* The "Capacity Limit" is strategy-independent. Whether the brain tries to predict efficiently or recruit effortfully, it cannot sustain the computation beyond the ~12-item threshold.

---

### Results Section 3: A Dynamical Escape (The Mechanism)

*Logic: Define the physical reality of "Giving Up." It's not just noise; it's a state change.*

* **Statistical Control (VIF):**
    * We rule out simple collinearity. The Variance Inflation Factor (VIF < 1.5) confirms that Length and Complexity remain statistically separable. The failure is biological, not mathematical.

* **The "Regime Shift" (PCA Trajectories):**
    * Determining *why* computation fails requires looking at the state space (Figure 3).
    * **Manifold Divergence:** In Short sequences, neural trajectories evolve along a "Computation Manifold." In Long sequences, they do not merely become noisier versions of this manifold—they **diverge** into an orthogonal region of state space (Max Dist: ~20.09).
    * *The Dynamical Interpretation:* The system undergoes a phase transition. Overwhelmed by memory load, the neural dynamics "escape" the attractor state required for active compression, settling into a robust, low-dimensional attractor state distinct from the computation manifold, characteristic of a 'passive' or 'overload' mode.

---

### Discussion: Stabilization of the Workspace

* **From "Software" to "Dynamics":** Our results shift the focus of evolutionary neuroscience. Macaques do not lack the "compression algorithm" *per se* (Result 1); they lack the **state-space stability** to maintain it over time (Result 3).
* **The Evolutionary Leap:** The transition to human-like "Language of Thought" may not have required the evolution of new grammar modules, but rather the expansion of a "Temporal Buffer"—the ability to stabilize the "Computation Manifold" against decay, allowing recursive rules to operate over longer timescales.