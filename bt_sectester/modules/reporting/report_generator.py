"""
Report generator for creating professional security assessment reports.

Generates PDF and HTML reports from session data.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from bt_sectester.utils.helpers import ensure_directory, sanitize_filename
from bt_sectester.utils.logger import LoggerMixin


class ReportGenerator(LoggerMixin):
    """Generator for security assessment reports."""

    def __init__(
        self,
        output_dir: Path = Path("reports"),
        company_name: str = "Security Assessment",
        logo_path: Optional[Path] = None,
    ):
        """
        Initialize report generator.

        Args:
            output_dir: Output directory for reports
            company_name: Company name for report header
            logo_path: Optional path to logo image
        """
        self.output_dir = output_dir
        self.company_name = company_name
        self.logo_path = logo_path

        ensure_directory(self.output_dir)

    def generate_pdf_report(
        self,
        session_data: Dict[str, Any],
        output_filename: Optional[str] = None,
        include_raw_logs: bool = False,
        ai_summary: Optional[str] = None,
    ) -> Path:
        """
        Generate PDF report from session data.

        Args:
            session_data: Session data dictionary
            output_filename: Custom output filename
            include_raw_logs: Whether to include raw logs
            ai_summary: Optional AI-generated summary

        Returns:
            Path to generated report
        """
        self.logger.info("Generating PDF report", session=session_data.get("session_id"))

        # Generate filename
        if output_filename is None:
            session_id = session_data.get("session_id", "report")
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            output_filename = f"bt_security_report_{session_id}_{timestamp}.pdf"

        output_filename = sanitize_filename(output_filename)
        output_path = self.output_dir / output_filename

        # Create PDF document
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )

        # Build content
        story = []
        styles = getSampleStyleSheet()

        # Title
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=24,
            textColor=colors.HexColor("#1a1a1a"),
            spaceAfter=30,
        )

        story.append(Paragraph("Bluetooth Security Assessment Report", title_style))
        story.append(Spacer(1, 0.2 * inch))

        # Metadata
        metadata = [
            ["Session ID:", session_data.get("session_id", "N/A")],
            ["Date:", session_data.get("start_time", datetime.utcnow().isoformat())],
            ["Company:", self.company_name],
            ["Generated:", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")],
        ]

        metadata_table = Table(metadata, colWidths=[2 * inch, 4 * inch])
        metadata_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )

        story.append(metadata_table)
        story.append(Spacer(1, 0.3 * inch))

        # AI Summary (if available)
        if ai_summary:
            story.append(Paragraph("Executive Summary", styles["Heading2"]))
            story.append(Spacer(1, 0.1 * inch))
            story.append(Paragraph(ai_summary, styles["BodyText"]))
            story.append(Spacer(1, 0.2 * inch))

        # Discovered Devices
        devices = session_data.get("devices", [])
        if devices:
            story.append(Paragraph(f"Discovered Devices ({len(devices)})", styles["Heading2"]))
            story.append(Spacer(1, 0.1 * inch))

            device_data = [["MAC Address", "Name", "Type", "Signal"]]
            for device in devices[:20]:  # Limit to first 20
                device_data.append(
                    [
                        device.get("mac", "N/A"),
                        device.get("name", "Unknown")[:30],
                        device.get("type", "N/A"),
                        f"{device.get('rssi', 'N/A')} dBm" if device.get("rssi") else "N/A",
                    ]
                )

            device_table = Table(device_data, colWidths=[1.5 * inch, 2 * inch, 1 * inch, 1 * inch])
            device_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ]
                )
            )

            story.append(device_table)
            story.append(Spacer(1, 0.2 * inch))

        # Attack Simulations
        attacks = session_data.get("attacks", [])
        if attacks:
            story.append(PageBreak())
            story.append(Paragraph(f"Security Simulations ({len(attacks)})", styles["Heading2"]))
            story.append(Spacer(1, 0.1 * inch))

            for idx, attack in enumerate(attacks, 1):
                story.append(Paragraph(f"Test {idx}: {attack.get('attack_type', 'Unknown')}", styles["Heading3"]))

                attack_details = [
                    ["Target:", attack.get("target", "N/A")],
                    ["Status:", attack.get("status", "N/A")],
                    ["Duration:", f"{attack.get('duration_seconds', 0):.2f} seconds"],
                ]

                # Add attack-specific details
                details = attack.get("details", {})
                for key, value in details.items():
                    attack_details.append([f"{key.replace('_', ' ').title()}:", str(value)])

                attack_table = Table(attack_details, colWidths=[2 * inch, 4 * inch])
                attack_table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                            ("GRID", (0, 0), (-1, -1), 1, colors.black),
                            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                            ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ]
                    )
                )

                story.append(attack_table)
                story.append(Spacer(1, 0.2 * inch))

        # Recommendations
        story.append(PageBreak())
        story.append(Paragraph("Recommendations", styles["Heading2"]))
        story.append(Spacer(1, 0.1 * inch))

        recommendations = [
            "Ensure all Bluetooth devices use strong PINs (6+ digits) and authentication.",
            "Disable Bluetooth when not in use to reduce attack surface.",
            "Keep device firmware updated to patch known vulnerabilities.",
            "Use Bluetooth 5.0+ with enhanced security features.",
            "Implement proper encryption for sensitive data transmission.",
            "Monitor for unauthorized Bluetooth devices in the environment.",
        ]

        for rec in recommendations:
            story.append(Paragraph(f"• {rec}", styles["BodyText"]))
            story.append(Spacer(1, 0.1 * inch))

        # Disclaimer
        story.append(Spacer(1, 0.3 * inch))
        disclaimer = """
        <b>Disclaimer:</b> This report is provided for authorized security testing purposes only.
        All tests were conducted with proper authorization. The findings represent potential
        vulnerabilities identified during the assessment period and should be addressed according
        to organizational risk management policies.
        """
        story.append(Paragraph(disclaimer, styles["BodyText"]))

        # Build PDF
        doc.build(story)

        self.logger.info("PDF report generated", output=str(output_path))
        return output_path

    def generate_html_report(
        self,
        session_data: Dict[str, Any],
        output_filename: Optional[str] = None,
    ) -> Path:
        """
        Generate HTML report from session data.

        Args:
            session_data: Session data dictionary
            output_filename: Custom output filename

        Returns:
            Path to generated report
        """
        self.logger.info("Generating HTML report", session=session_data.get("session_id"))

        # Generate filename
        if output_filename is None:
            session_id = session_data.get("session_id", "report")
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            output_filename = f"bt_security_report_{session_id}_{timestamp}.html"

        output_filename = sanitize_filename(output_filename)
        output_path = self.output_dir / output_filename

        # Generate HTML content
        html_content = self._generate_html(session_data)

        # Write to file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        self.logger.info("HTML report generated", output=str(output_path))
        return output_path

    def _generate_html(self, session_data: Dict[str, Any]) -> str:
        """
        Generate HTML content for report.

        Args:
            session_data: Session data dictionary

        Returns:
            HTML string
        """
        devices = session_data.get("devices", [])
        attacks = session_data.get("attacks", [])

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bluetooth Security Assessment Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #1a1a1a;
            border-bottom: 3px solid #007bff;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #333;
            margin-top: 30px;
        }}
        .metadata {{
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background-color: white;
            margin-bottom: 20px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #007bff;
            color: white;
        }}
        .status-success {{
            color: #28a745;
            font-weight: bold;
        }}
        .status-failed {{
            color: #dc3545;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <h1>Bluetooth Security Assessment Report</h1>

    <div class="metadata">
        <p><strong>Session ID:</strong> {session_data.get('session_id', 'N/A')}</p>
        <p><strong>Date:</strong> {session_data.get('start_time', 'N/A')}</p>
        <p><strong>Company:</strong> {self.company_name}</p>
        <p><strong>Generated:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
    </div>

    <h2>Discovered Devices ({len(devices)})</h2>
    <table>
        <thead>
            <tr>
                <th>MAC Address</th>
                <th>Name</th>
                <th>Type</th>
                <th>Signal (RSSI)</th>
            </tr>
        </thead>
        <tbody>
        """

        for device in devices[:20]:
            html += f"""
            <tr>
                <td>{device.get('mac', 'N/A')}</td>
                <td>{device.get('name', 'Unknown')}</td>
                <td>{device.get('type', 'N/A')}</td>
                <td>{device.get('rssi', 'N/A')} dBm</td>
            </tr>
            """

        html += """
        </tbody>
    </table>

    <h2>Security Simulations</h2>
        """

        for attack in attacks:
            status_class = "status-success" if attack.get("status") == "success" else "status-failed"
            html += f"""
    <div class="metadata">
        <h3>{attack.get('attack_type', 'Unknown')}</h3>
        <p><strong>Target:</strong> {attack.get('target', 'N/A')}</p>
        <p><strong>Status:</strong> <span class="{status_class}">{attack.get('status', 'N/A')}</span></p>
        <p><strong>Duration:</strong> {attack.get('duration_seconds', 0):.2f} seconds</p>
    </div>
            """

        html += """
</body>
</html>
        """

        return html
