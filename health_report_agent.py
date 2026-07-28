from __future__ import annotations

import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, List

import aiohttp
import aiohttp.web
from pydantic import ValidationError

sys.path.insert(0, os.getcwd())
from models import HealthData, HealthMetricStatus, HealthReport


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class CaregiverAgent:
    """Simulates a caregiver receiving reports from the Health Report Agent."""

    async def receive_report(self, report: HealthReport) -> None:
        logging.info("Caregiver Agent received report for %s", report.patient_name)
        logging.info("Caregiver Agent will follow up with recommended care.")


class EmergencyResponseAgent:
    """Simulates an emergency response agent that receives urgent health reports."""

    async def receive_report(self, report: HealthReport) -> None:
        logging.warning("Emergency Response Agent received CRITICAL report for %s", report.patient_name)
        logging.warning("Emergency services would be notified in a live deployment.")


class HealthDashboard:
    """A lightweight professional dashboard for previewing the latest health report."""

    def __init__(self, agent: "HealthReportAgent") -> None:
        self.agent = agent
        self.app = aiohttp.web.Application()
        self.app.add_routes(
            [
                aiohttp.web.get("/", self.handle_home),
                aiohttp.web.get("/dashboard", self.handle_dashboard),
                aiohttp.web.get("/api/report", self.handle_report_json),
            ]
        )
        self.runner: aiohttp.web.AppRunner | None = None

    async def start(self) -> None:
        self.runner = aiohttp.web.AppRunner(self.app)
        await self.runner.setup()
        site = aiohttp.web.TCPSite(self.runner, "127.0.0.1", 8080)
        await site.start()
        logging.info("Professional UI dashboard available at http://127.0.0.1:8080/dashboard")

    async def handle_home(self, request: aiohttp.web.Request) -> aiohttp.web.Response:
        raise aiohttp.web.HTTPFound("/dashboard")

    async def handle_dashboard(self, request: aiohttp.web.Request) -> aiohttp.web.Response:
        html = self.render_dashboard()
        return aiohttp.web.Response(text=html, content_type="text/html")

    async def handle_report_json(self, request: aiohttp.web.Request) -> aiohttp.web.Response:
        report = self.agent.latest_report
        if report is None:
            return aiohttp.web.json_response({"message": "No report available yet."}, status=404)
        return aiohttp.web.json_response(report.model_dump())

    def render_dashboard(self) -> str:
        report = self.agent.latest_report
        if report is None:
            return (
                "<html><head><title>Health Report Dashboard</title></head>"
                "<body style='font-family:Arial,sans-serif; margin:40px;'>"
                "<h1>Health Report Agent Dashboard</h1>"
                "<p>No health report has been generated yet.</p>"
                "</body></html>"
            )

        metric_rows = "".join(
            f"<tr><td><strong>{label}</strong></td><td>{value}</td></tr>"
            for label, value in report.metrics.items()
        )
        analysis_rows = "".join(
            f"<tr><td><strong>{label}</strong></td><td>{value}</td></tr>"
            for label, value in report.analysis.items()
        )
        recommendations = "".join(f"<li>{item}</li>" for item in report.recommendations)
        timestamp = report.timestamp.strftime("%Y-%m-%d %I:%M %p")

        return f"""
        <html>
        <head>
            <title>Health Report Dashboard</title>
            <style>
                body {{ font-family: Arial, sans-serif; background:#f6f8fa; color:#222; padding:24px; }}
                .container {{ max-width:980px; margin:auto; background:#fff; border-radius:14px; box-shadow:0 18px 45px rgba(0,0,0,0.08); padding:32px; }}
                h1 {{ margin-bottom:4px; color:#1b2838; }}
                .tag {{ display:inline-block; padding:8px 14px; border-radius:999px; background:#e6f2ff; color:#115293; font-size:0.95rem; }}
                table {{ width:100%; border-collapse:collapse; margin-top:16px; }}
                td {{ padding:10px 12px; border-bottom:1px solid #eceff4; }}
                th {{ text-align:left; padding:12px; color:#0f172a; }}
                .section {{ margin-top:28px; }}
                .reco {{ margin-top:12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Health Report for {report.patient_name}</h1>
                <p class="tag">Status: {report.overall_status} • Risk: {report.risk_level}</p>
                <div class="section">
                    <h2>Key Metrics</h2>
                    <table>
                        {metric_rows}
                    </table>
                </div>
                <div class="section">
                    <h2>Metric Analysis</h2>
                    <table>
                        {analysis_rows}
                    </table>
                </div>
                <div class="section">
                    <h2>Recommendations</h2>
                    <ul class="reco">
                        {recommendations}
                    </ul>
                </div>
                <div class="section">
                    <p><strong>Report ID:</strong> {report.report_id}</p>
                    <p><strong>Generated:</strong> {timestamp}</p>
                </div>
            </div>
        </body>
        </html>
        """


class HealthReportAgent:
    """Health Report Agent that analyzes wearable health data and forwards reports."""

    def __init__(self) -> None:
        self.caregiver_agent = CaregiverAgent()
        self.emergency_agent = EmergencyResponseAgent()
        self.latest_report: HealthReport | None = None
        self.dashboard = HealthDashboard(self)

    async def start(self) -> None:
        logging.info("Health Report Agent started.")
        await self.dashboard.start()

    async def receive_health_data(self, payload: Dict[str, Any]) -> HealthReport:
        logging.info("Received health data payload.")
        try:
            health_data = HealthData.model_validate(payload)
        except ValidationError as exc:
            logging.error("Health data validation failed: %s", exc)
            raise

        logging.info("Analyzing metrics for %s", health_data.patient_name)
        report = self.generate_health_report(health_data)
        self.latest_report = report
        logging.info("Health report generated: %s", report.report_id)

        await self.dispatch_report(report)
        return report

    def generate_health_report(self, health_data: HealthData) -> HealthReport:
        metric_status = {
            "Heart Rate": self.analyze_heart_rate(health_data.heart_rate),
            "SpO2": self.analyze_spo2(health_data.spo2),
            "Temperature": self.analyze_temperature(health_data.body_temperature),
            "Blood Pressure": self.analyze_blood_pressure(health_data.blood_pressure),
            "Activity": self.analyze_steps(health_data.steps),
            "Sleep Quality": self.analyze_sleep(health_data.sleep_hours),
        }

        abnormal_count = sum(1 for status in metric_status.values() if status not in {HealthMetricStatus.NORMAL, HealthMetricStatus.ACTIVE})
        spo2_critical = health_data.spo2 < 90

        overall_status, risk_level = self.classify_risk(abnormal_count, spo2_critical)
        recommendations = self.build_recommendations(overall_status)

        metrics = {
            "Heart Rate": f"{health_data.heart_rate} bpm",
            "SpO2": f"{health_data.spo2}%",
            "Temperature": f"{health_data.body_temperature:.1f} °C",
            "Blood Pressure": health_data.blood_pressure,
            "Steps": str(health_data.steps),
            "Sleep Hours": f"{health_data.sleep_hours:.1f}",
        }

        summary = (
            f"{health_data.patient_name} is classified as {overall_status} with {risk_level} risk. "
            f"The report contains actionable guidance for caregiver or emergency response follow-up."
        )

        return HealthReport(
            patient_name=health_data.patient_name,
            age=health_data.age,
            timestamp=health_data.timestamp,
            metrics=metrics,
            analysis={key: status.value for key, status in metric_status.items()},
            overall_status=overall_status,
            risk_level=risk_level,
            recommendations=recommendations,
            summary=summary,
        )

    def analyze_heart_rate(self, heart_rate: int) -> HealthMetricStatus:
        if heart_rate < 60:
            return HealthMetricStatus.LOW
        if heart_rate <= 100:
            return HealthMetricStatus.NORMAL
        return HealthMetricStatus.HIGH

    def analyze_spo2(self, spo2: int) -> HealthMetricStatus:
        if spo2 >= 95:
            return HealthMetricStatus.NORMAL
        if spo2 >= 90:
            return HealthMetricStatus.LOW
        return HealthMetricStatus.CRITICAL

    def analyze_temperature(self, temperature: float) -> HealthMetricStatus:
        if 36.5 <= temperature <= 37.5:
            return HealthMetricStatus.NORMAL
        return HealthMetricStatus.FEVER

    def analyze_blood_pressure(self, blood_pressure: str) -> HealthMetricStatus:
        try:
            systolic, diastolic = (int(value) for value in blood_pressure.split("/"))
        except ValueError:
            logging.error("Invalid blood pressure format: %s", blood_pressure)
            return HealthMetricStatus.HIGH

        if systolic < 140 and diastolic < 90:
            return HealthMetricStatus.NORMAL
        return HealthMetricStatus.HIGH

    def analyze_steps(self, steps: int) -> HealthMetricStatus:
        if steps >= 6000:
            return HealthMetricStatus.ACTIVE
        return HealthMetricStatus.LOW_ACTIVITY

    def analyze_sleep(self, sleep_hours: float) -> HealthMetricStatus:
        if sleep_hours >= 7:
            return HealthMetricStatus.NORMAL
        if sleep_hours >= 5:
            return HealthMetricStatus.FAIR
        return HealthMetricStatus.POOR

    def classify_risk(self, abnormal_count: int, spo2_critical: bool) -> tuple[str, str]:
        if spo2_critical or abnormal_count >= 3:
            return "Critical", "High"
        if abnormal_count in {1, 2}:
            return "Needs Monitoring", "Medium"
        return "Healthy", "Low"

    def build_recommendations(self, overall_status: str) -> List[str]:
        if overall_status == "Healthy":
            return [
                "Continue regular exercise.",
                "Stay hydrated.",
                "Maintain healthy sleep.",
            ]
        if overall_status == "Needs Monitoring":
            return [
                "Monitor blood pressure.",
                "Increase daily walking.",
                "Improve sleep schedule.",
                "Drink enough water.",
            ]
        return [
            "Contact caregiver immediately.",
            "Seek medical attention.",
            "Monitor oxygen saturation.",
            "Avoid strenuous activity.",
        ]

    async def dispatch_report(self, report: HealthReport) -> None:
        if report.risk_level == "High":
            logging.info("Dispatching report to Emergency Response Agent.")
            await self.emergency_agent.receive_report(report)
        else:
            logging.info("Dispatching report to Caregiver Agent.")
            await self.caregiver_agent.receive_report(report)

    async def run_demo(self) -> None:
        sample_payload = {
            "patient_name": "John",
            "age": 72,
            "heart_rate": 108,
            "spo2": 91,
            "body_temperature": 38.4,
            "blood_pressure": "150/95",
            "steps": 1800,
            "sleep_hours": 5,
            "timestamp": datetime.utcnow().isoformat(),
        }

        report = await self.receive_health_data(sample_payload)
        self.print_report_console(report)

    def print_report_console(self, report: HealthReport) -> None:
        logging.info("Printing structured health report to console.")
        separator = "=" * 41
        print(f"\n{separator}")
        print("HEALTH REPORT")
        print(f"{separator}\n")
        print("Patient")
        print("-------")
        print(f"Name : {report.patient_name}")
        print(f"Age  : {report.age}\n")
        print("Health Metrics")
        print("--------------")
        for label, value in report.metrics.items():
            print(f"{label.ljust(16)}: {value}")
        print("\nAnalysis")
        print("--------")
        for label, value in report.analysis.items():
            print(f"{label.ljust(16)}: {value}")
        print("\nOverall Status")
        print("--------------")
        print(f"Health Status : {report.overall_status}")
        print(f"Risk Level    : {report.risk_level}\n")
        print("Recommendations")
        print("---------------")
        for item in report.recommendations:
            print(f"✓ {item}")
        print("\nTimestamp")
        print("---------")
        print(report.timestamp.strftime("%Y-%m-%d %I:%M %p"))
        print(f"\n{separator}\n")


async def main() -> None:
    agent = HealthReportAgent()
    await agent.start()
    await agent.run_demo()

    # Keep the dashboard alive until the user cancels the program.
    logging.info("Health Report Agent is running. Press Ctrl+C to exit.")
    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Health Report Agent shutting down.")
