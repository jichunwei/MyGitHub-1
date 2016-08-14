package ginkgoTest

import (
	. "github.com/onsi/ginkgo"
	. "github.com/onsi/gomega"
)

var _ = Describe("ScoreKeeper", func() {
	var scoreKeeper *ScoreKeeper

	BeforeEach(func() {
		var err error
		scoreKeeper, err = NewScoreKeeper("Denver Broncos")
		Expect(err).NotTo(HaveOccured())
	})

	It("should have a starting score of 0", func() {
		Expect(scoreKeeper.Score).To(Equal(0))
	})

	Context("when a touchdown is scored", func() {
		BeforeEach(func() {
			scoreKeeper.Touchdown("Manning")
		})

		It("should increment the score", func() {
			Expect(scoreKeeper.Score).To(Equal(6))
		})

		It("should update the scoring player's stats", func() {
			Expect(scoreKeeper.Stats).To(HaveKey("Manning"))
			Expect(scoreKeeper.Stats["Manning"]["Touchdowns"]).To(Equal(1))
			Expect(scoreKeeper.Stats["Manning"]["Points"]).To(Equal(6))
		})
	})
})