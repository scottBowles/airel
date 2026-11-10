import List from '@lucide/svelte/icons/list';
import Route from '@lucide/svelte/icons/route';
import Orbit from '@lucide/svelte/icons/orbit';
import Milestone from '@lucide/svelte/icons/milestone';
import BookOpen from '@lucide/svelte/icons/book-open';
import MonitorPlay from '@lucide/svelte/icons/monitor-play';
import Waypoints from '@lucide/svelte/icons/waypoints';
import Map from '@lucide/svelte/icons/map';
import CalendarDays from '@lucide/svelte/icons/calendar-days';
import LayoutGrid from '@lucide/svelte/icons/layout-grid';
import type { ChronicleViewId } from '$lib/chronicle/views';

export const VIEW_ICONS: Record<ChronicleViewId, typeof List> = {
	classic: List,
	voyage: Route,
	starchart: Orbit,
	timeline: Milestone,
	saga: BookOpen,
	replay: MonitorPlay,
	threads: Waypoints,
	atlas: Map,
	calendar: CalendarDays,
	deck: LayoutGrid
};
