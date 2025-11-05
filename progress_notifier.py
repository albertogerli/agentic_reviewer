"""
Progress Tracking and Notification System
Provides visual progress feedback and system notifications.
"""

import sys
import platform
import subprocess
import logging
from typing import Optional, List
from datetime import datetime
from tqdm import tqdm
import time

logger = logging.getLogger(__name__)


class ProgressTracker:
    """
    Manages progress bars for different phases of document review.
    """
    
    def __init__(self, total_steps: int = 100, desc: str = "Processing"):
        self.total_steps = total_steps
        self.desc = desc
        self.pbar: Optional[tqdm] = None
        self.current_step = 0
        self.start_time = None
        self.phase_times = {}
    
    def start(self):
        """Start the progress bar."""
        self.pbar = tqdm(
            total=self.total_steps,
            desc=self.desc,
            unit="step",
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]',
            colour='green',
            ncols=100
        )
        self.start_time = datetime.now()
        logger.info(f"Progress tracking started: {self.desc}")
    
    def update(self, steps: int = 1, description: Optional[str] = None):
        """Update progress bar."""
        if self.pbar:
            self.pbar.update(steps)
            self.current_step += steps
            
            if description:
                self.pbar.set_description(description)
    
    def set_phase(self, phase_name: str, steps: int = 1):
        """Set current phase and update."""
        phase_start = datetime.now()
        if self.pbar:
            self.pbar.set_description(f"{phase_name}")
            self.pbar.update(steps)
            self.current_step += steps
        
        # Track phase timing
        if phase_name not in self.phase_times:
            self.phase_times[phase_name] = []
        self.phase_times[phase_name].append(phase_start)
    
    def complete(self, message: Optional[str] = None):
        """Complete the progress bar."""
        if self.pbar:
            self.pbar.n = self.total_steps
            self.pbar.refresh()
            if message:
                self.pbar.set_description(message)
            self.pbar.close()
        
        if self.start_time:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            logger.info(f"Progress completed in {elapsed:.1f}s")
    
    def close(self):
        """Close progress bar."""
        if self.pbar:
            self.pbar.close()
    
    def get_elapsed_time(self) -> float:
        """Get elapsed time in seconds."""
        if self.start_time:
            return (datetime.now() - self.start_time).total_seconds()
        return 0.0
    
    def get_eta(self) -> str:
        """Get estimated time of arrival."""
        if not self.pbar or self.current_step == 0:
            return "unknown"
        
        elapsed = self.get_elapsed_time()
        steps_per_second = self.current_step / elapsed if elapsed > 0 else 0
        remaining_steps = self.total_steps - self.current_step
        
        if steps_per_second > 0:
            eta_seconds = remaining_steps / steps_per_second
            if eta_seconds < 60:
                return f"{int(eta_seconds)}s"
            elif eta_seconds < 3600:
                return f"{int(eta_seconds/60)}m {int(eta_seconds%60)}s"
            else:
                hours = int(eta_seconds / 3600)
                minutes = int((eta_seconds % 3600) / 60)
                return f"{hours}h {minutes}m"
        
        return "calculating..."


class MultiPhaseProgress:
    """
    Manages progress across multiple phases with nested progress bars.
    """
    
    def __init__(self, phases: List[tuple]):
        """
        Initialize with list of (phase_name, steps) tuples.
        Example: [("Classification", 10), ("Review", 50), ("Refinement", 40)]
        """
        self.phases = phases
        self.total_steps = sum(steps for _, steps in phases)
        self.main_pbar: Optional[tqdm] = None
        self.phase_pbar: Optional[tqdm] = None
        self.current_phase_idx = 0
        self.phase_start_times = []
    
    def start(self):
        """Start the multi-phase progress tracking."""
        self.main_pbar = tqdm(
            total=self.total_steps,
            desc="Overall Progress",
            position=0,
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]',
            colour='blue',
            ncols=100
        )
    
    def start_phase(self, phase_idx: int):
        """Start a specific phase."""
        if phase_idx >= len(self.phases):
            return
        
        phase_name, phase_steps = self.phases[phase_idx]
        self.current_phase_idx = phase_idx
        self.phase_start_times.append(datetime.now())
        
        # Close previous phase bar if exists
        if self.phase_pbar:
            self.phase_pbar.close()
        
        # Create new phase bar
        self.phase_pbar = tqdm(
            total=phase_steps,
            desc=f"  └─ {phase_name}",
            position=1,
            leave=False,
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}',
            colour='green',
            ncols=100
        )
    
    def update_phase(self, steps: int = 1, sub_description: Optional[str] = None):
        """Update current phase progress."""
        if self.phase_pbar:
            self.phase_pbar.update(steps)
            if sub_description:
                phase_name, _ = self.phases[self.current_phase_idx]
                self.phase_pbar.set_description(f"  └─ {phase_name}: {sub_description}")
        
        if self.main_pbar:
            self.main_pbar.update(steps)
    
    def complete_phase(self):
        """Complete current phase and move to next."""
        if self.phase_pbar:
            # Fill remaining steps
            remaining = self.phase_pbar.total - self.phase_pbar.n
            if remaining > 0:
                self.phase_pbar.update(remaining)
                if self.main_pbar:
                    self.main_pbar.update(remaining)
            
            self.phase_pbar.close()
            self.phase_pbar = None
    
    def complete(self):
        """Complete all progress tracking."""
        if self.phase_pbar:
            self.phase_pbar.close()
        
        if self.main_pbar:
            # Fill to 100%
            remaining = self.main_pbar.total - self.main_pbar.n
            if remaining > 0:
                self.main_pbar.update(remaining)
            self.main_pbar.close()


class SystemNotifier:
    """
    Sends system notifications using native OS notification systems.
    """
    
    def __init__(self, app_name: str = "Document Reviewer"):
        self.app_name = app_name
        self.os_type = platform.system()
        self.notifications_enabled = self._check_notification_support()
    
    def _check_notification_support(self) -> bool:
        """Check if system notifications are supported."""
        if self.os_type == "Darwin":  # macOS
            return True
        elif self.os_type == "Linux":
            # Check if notify-send is available
            try:
                subprocess.run(['which', 'notify-send'], 
                             capture_output=True, check=True, timeout=2)
                return True
            except:
                return False
        elif self.os_type == "Windows":
            # Windows 10+ has native notifications
            return True
        
        return False
    
    def send(self, title: str, message: str, urgency: str = "normal"):
        """
        Send a system notification.
        
        Args:
            title: Notification title
            message: Notification message
            urgency: "low", "normal", or "critical"
        """
        if not self.notifications_enabled:
            logger.debug(f"Notifications not supported: {title} - {message}")
            return
        
        try:
            if self.os_type == "Darwin":  # macOS
                self._send_macos(title, message)
            elif self.os_type == "Linux":
                self._send_linux(title, message, urgency)
            elif self.os_type == "Windows":
                self._send_windows(title, message)
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
    
    def _send_macos(self, title: str, message: str):
        """Send notification on macOS using osascript."""
        script = f'''
        display notification "{message}" with title "{self.app_name}" subtitle "{title}"
        '''
        subprocess.run(['osascript', '-e', script], capture_output=True)
        logger.info(f"macOS notification sent: {title}")
    
    def _send_linux(self, title: str, message: str, urgency: str):
        """Send notification on Linux using notify-send."""
        subprocess.run([
            'notify-send',
            '-u', urgency,
            '-a', self.app_name,
            title,
            message
        ], capture_output=True)
        logger.info(f"Linux notification sent: {title}")
    
    def _send_windows(self, title: str, message: str):
        """Send notification on Windows using PowerShell."""
        # Use Windows Toast notification
        script = f'''
        [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
        $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
        $toastXml = [xml] $template.GetXml()
        $toastXml.GetElementsByTagName("text")[0].AppendChild($toastXml.CreateTextNode("{title}")) > $null
        $toastXml.GetElementsByTagName("text")[1].AppendChild($toastXml.CreateTextNode("{message}")) > $null
        $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
        $xml.LoadXml($toastXml.OuterXml)
        $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
        [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("{self.app_name}").Show($toast)
        '''
        subprocess.run(['powershell', '-Command', script], capture_output=True)
        logger.info(f"Windows notification sent: {title}")
    
    def notify_start(self, document_title: str):
        """Notify that review has started."""
        self.send(
            "Review Started",
            f"Processing: {document_title}",
            urgency="low"
        )
    
    def notify_complete(self, document_title: str, score: float, time_taken: str):
        """Notify that review is complete."""
        self.send(
            "Review Complete! ✅",
            f"{document_title}\nScore: {score}/100\nTime: {time_taken}",
            urgency="normal"
        )
    
    def notify_error(self, document_title: str, error_message: str):
        """Notify that an error occurred."""
        self.send(
            "Review Error ❌",
            f"{document_title}\nError: {error_message}",
            urgency="critical"
        )
    
    def notify_checkpoint(self, document_title: str, iteration: int):
        """Notify that a checkpoint was saved."""
        self.send(
            "Checkpoint Saved",
            f"{document_title}\nIteration {iteration} saved - can resume later",
            urgency="low"
        )
    
    def notify_iteration_complete(self, document_title: str, iteration: int, score: float):
        """Notify that an iteration is complete."""
        self.send(
            f"Iteration {iteration} Complete",
            f"{document_title}\nCurrent score: {score}/100",
            urgency="low"
        )


class ReviewProgressOrchestrator:
    """
    Orchestrates progress tracking and notifications for the entire review process.
    """
    
    def __init__(self, document_title: str, mode: str = "iterative", 
                 max_iterations: int = 3, enable_notifications: bool = True):
        self.document_title = document_title
        self.mode = mode
        self.max_iterations = max_iterations
        self.enable_notifications = enable_notifications
        
        # Calculate phases based on mode
        self.phases = self._calculate_phases()
        
        # Initialize components
        self.progress = MultiPhaseProgress(self.phases)
        self.notifier = SystemNotifier() if enable_notifications else None
        self.start_time = None
    
    def _calculate_phases(self) -> List[tuple]:
        """Calculate phases based on review mode."""
        if self.mode == "standard":
            return [
                ("Document Analysis", 10),
                ("Agent Reviews", 80),
                ("Report Generation", 10)
            ]
        elif self.mode == "iterative":
            phases = [("Document Classification", 5)]
            
            # Add phases for each iteration
            steps_per_iteration = 90 // self.max_iterations
            for i in range(1, self.max_iterations + 1):
                phases.append((f"Iteration {i}: Review", steps_per_iteration // 2))
                phases.append((f"Iteration {i}: Improve", steps_per_iteration // 2))
            
            phases.append(("Final Reports", 5))
            return phases
        else:  # interactive
            phases = [
                ("Document Classification", 5),
                ("Initial Review", 15)
            ]
            
            if self.max_iterations > 0:
                phases.append(("Collecting User Input", 10))
                
                steps_per_iteration = 60 // self.max_iterations
                for i in range(1, self.max_iterations + 1):
                    phases.append((f"Iteration {i}: Review", steps_per_iteration // 2))
                    phases.append((f"Iteration {i}: Improve", steps_per_iteration // 2))
            
            phases.append(("Final Reports", 10))
            return phases
    
    def start(self):
        """Start the review process."""
        self.start_time = datetime.now()
        self.progress.start()
        
        if self.notifier:
            self.notifier.notify_start(self.document_title)
        
        logger.info(f"Review orchestration started for: {self.document_title}")
    
    def start_phase(self, phase_name: str):
        """Start a specific phase."""
        # Find phase index
        phase_idx = None
        for idx, (name, _) in enumerate(self.phases):
            if name == phase_name or name.startswith(phase_name):
                phase_idx = idx
                break
        
        if phase_idx is not None:
            self.progress.start_phase(phase_idx)
    
    def update(self, steps: int = 1, description: Optional[str] = None):
        """Update current phase."""
        self.progress.update_phase(steps, description)
    
    def complete_phase(self):
        """Complete current phase."""
        self.progress.complete_phase()
    
    def complete(self, final_score: float):
        """Complete the review process."""
        self.progress.complete()
        
        if self.start_time and self.notifier:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            time_str = self._format_time(elapsed)
            self.notifier.notify_complete(self.document_title, final_score, time_str)
        
        logger.info(f"Review orchestration completed: {self.document_title}")
    
    def notify_checkpoint(self, iteration: int):
        """Send checkpoint notification."""
        if self.notifier:
            self.notifier.notify_checkpoint(self.document_title, iteration)
    
    def notify_iteration_complete(self, iteration: int, score: float):
        """Send iteration complete notification."""
        if self.notifier:
            self.notifier.notify_iteration_complete(self.document_title, iteration, score)
    
    def notify_error(self, error_message: str):
        """Send error notification."""
        if self.notifier:
            self.notifier.notify_error(self.document_title, error_message)
    
    def _format_time(self, seconds: float) -> str:
        """Format elapsed time."""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            mins = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{mins}m {secs}s"
        else:
            hours = int(seconds / 3600)
            mins = int((seconds % 3600) / 60)
            return f"{hours}h {mins}m"

