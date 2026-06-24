declare module 'maplibre-gl' {
  // This is a minimal declaration file for maplibre-gl to suppress TypeScript errors.
  // The actual types are not needed for the code to work, so we declare everything as `any`.
  
  export const version: string;
  export function setRTLTextPlugin(url: string, callback: (error?: Error) => void, deferred?: boolean): void;
  
  export class Map {
    constructor(options: any);
    on(event: string, handler: (e: any) => void): void;
    off(event: string, handler: (e: any) => void): void;
    remove(): void;
    getCanvas(): HTMLCanvasElement;
    getBounds(): any;
    getCenter(): { lng: number; lat: number };
    getZoom(): number;
    getBearing(): number;
    getPitch(): number;
    setCenter(center: [number, number]): void;
    setZoom(zoom: number): void;
    setBearing(bearing: number): void;
    setPitch(pitch: number): void;
    flyTo(options: any): void;
    easeTo(options: any): void;
    jumpTo(options: any): void;
    addLayer(layer: any, beforeId?: string): void;
    removeLayer(id: string): void;
    getLayer(id: string): any;
    addSource(id: string, source: any): void;
    removeSource(id: string): void;
    getSource(id: string): any;
    addControl(control: any, position?: string): void;
    removeControl(control: any): void;
    hasControl(control: any): boolean;
    project(lngLat: [number, number]): { x: number; y: number };
    unproject(point: [number, number]): { lng: number; lat: number };
    queryRenderedFeatures(point: [number, number] | [number, number][], options?: any): any[];
    resize(): void;
    getContainer(): HTMLElement;
    getStyle(): any;
    setStyle(style: any): void;
    isStyleLoaded(): boolean;
    once(event: string, handler: (e: any) => void): void;
    getMaxZoom(): number;
    getMinZoom(): number;
    doubleClickZoom: { enable(): void; disable(): void };
    isMoving(): boolean;
    showTileBoundaries: boolean;
    showCollisionBoxes: boolean;
    showPadding: boolean;
    showTerrainWireframe: boolean;
    showOverdrawInspector: boolean;
  }

  export class NavigationControl {
    constructor(options?: any);
  }

  export class ScaleControl {
    constructor(options?: any);
  }

  export class FullscreenControl {
    constructor(options?: any);
  }

  export class GeolocateControl {
    constructor(options?: any);
  }

  export class AttributionControl {
    constructor(options?: any);
  }

  export class Popup {
    constructor(options?: any);
    addTo(map: Map): this;
    remove(): this;
    setLngLat(lngLat: [number, number]): this;
    setText(text: string): this;
    setHTML(html: string): this;
    setDOMContent(html: Node): this;
    getElement(): HTMLElement;
  }

  export class Marker {
    constructor(element?: HTMLElement, options?: any);
    addTo(map: Map): this;
    remove(): this;
    setLngLat(lngLat: [number, number]): this;
    getLngLat(): { lng: number; lat: number };
    setPopup(popup: Popup): this;
    togglePopup(): this;
    getPopup(): Popup | undefined;
    setDraggable(shouldBeDraggable: boolean): this;
    isDraggable(): boolean;
    drag(): void;
  }

  export class LngLat {
    constructor(lng: number, lat: number);
    lng: number;
    lat: number;
    wrap(): LngLat;
    toArray(): [number, number];
    distanceTo(other: LngLat): number;
    toBounds(radius: number): any;
    static convert(input: [number, number] | { lng: number; lat: number } | LngLat): LngLat;
  }

  export class LngLatBounds {
    constructor(bounds?: [number, number, number, number] | [LngLat, LngLat]);
    extend(obj: LngLat | LngLatBounds): this;
    getCenter(): LngLat;
    getSouthWest(): LngLat;
    getNorthEast(): LngLat;
    getNorthWest(): LngLat;
    getSouthEast(): LngLat;
    toArray(): [number, number, number, number];
    toSW(): [number, number];
    toNE(): [number, number];
    isEmpty(): boolean;
    contains(lngLat: LngLat): boolean;
    toString(): string;
    static convert(input: any): LngLatBounds;
  }

  export interface GeoJSONSource {
    type: 'geojson';
    data: any;
    cluster?: boolean;
    clusterMaxZoom?: number;
    clusterRadius?: number;
  }

  export interface MapMouseEvent {
    type: string;
    target: Map;
    originalEvent: MouseEvent;
    point: { x: number; y: number };
    lngLat: LngLat;
  }

  export interface IControl {
    onAdd(map: Map): HTMLElement;
    onRemove(map: Map): void;
    getDefaultPosition?(): string;
  }

  export function addProtocol(name: string, handler: any): void;
  export function removeProtocol(name: string): void;
  
  export function supported(): boolean;
  export function clearPrewarms(): void;
  export function clearStorage(): void;
  
  export const MapMouseEvent: any;
  export const MapTouchEvent: any;
  export const MapWheelEvent: any;
  export const MapBoxZoomEvent: any;
  
  export type RequestParameters = any;
  export type ResponseCallback = any;
}
