import logging

logger = logging.getLogger(__name__)

class VisualGenerationReport:
    def __init__(self):
        self.total_frames_generated = 0
        self.successful_generations = 0
        self.failed_generations = 0

    def log_frame_generation(self, success: bool):
        self.total_frames_generated += 1
        if success:
            self.successful_generations += 1
            logger.info("Frame generated successfully.")
        else:
            self.failed_generations += 1
            logger.error("Frame generation failed.")

    def generate_report(self):
        report = (
            f"Visual Generation Report:\n"
            f"Total Frames Generated: {self.total_frames_generated}\n"
            f"Successful Generations: {self.successful_generations}\n"
            f"Failed Generations: {self.failed_generations}\n"
        )
        logger.info(report)
        return report

# Example usage
if __name__ == "__main__":
    report = VisualGenerationReport()
    report.log_frame_generation(True)  # Simulate a successful generation
    report.log_frame_generation(False)  # Simulate a failed generation
    print(report.generate_report())
