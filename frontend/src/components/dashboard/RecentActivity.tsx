import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { formatDistanceToNow } from 'date-fns'
import { it } from 'date-fns/locale'
import { 
  Instagram, 
  FileText, 
  Calendar,
  Image,
  TrendingUp,
  Clock
} from 'lucide-react'

interface ActivityItem {
  id: string
  type: 'post_published' | 'post_scheduled' | 'media_uploaded' | 'account_connected' | 'analytics_synced'
  title: string
  description: string
  timestamp: string
  metadata?: {
    account_username?: string
    account_avatar?: string
    post_type?: string
    media_count?: number
  }
}

interface RecentActivityProps {
  activities: ActivityItem[]
  className?: string
}

const getActivityIcon = (type: string) => {
  switch (type) {
    case 'post_published':
      return FileText
    case 'post_scheduled':
      return Calendar
    case 'media_uploaded':
      return Image
    case 'account_connected':
      return Instagram
    case 'analytics_synced':
      return TrendingUp
    default:
      return Clock
  }
}

const getActivityColor = (type: string) => {
  switch (type) {
    case 'post_published':
      return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
    case 'post_scheduled':
      return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300'
    case 'media_uploaded':
      return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300'
    case 'account_connected':
      return 'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-300'
    case 'analytics_synced':
      return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300'
    default:
      return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300'
  }
}

const RecentActivity: React.FC<RecentActivityProps> = ({ activities, className }) => {
  if (!activities.length) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>Attività Recenti</CardTitle>
          <CardDescription>Nessuna attività recente</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-6 text-muted-foreground">
            <Clock className="mx-auto h-12 w-12 mb-4 opacity-50" />
            <p>Nessuna attività da visualizzare</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>Attività Recenti</CardTitle>
        <CardDescription>
          Ultime azioni sui tuoi account Instagram
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {activities.slice(0, 8).map((activity) => {
            const Icon = getActivityIcon(activity.type)
            
            return (
              <div key={activity.id} className="flex items-start space-x-4">
                <div className="relative flex-shrink-0">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-muted">
                    <Icon className="h-5 w-5" />
                  </div>
                  {activity.metadata?.account_avatar && (
                    <Avatar className="absolute -bottom-1 -right-1 h-6 w-6 border-2 border-background">
                      <AvatarImage src={activity.metadata.account_avatar} />
                      <AvatarFallback className="text-xs">
                        {activity.metadata.account_username?.charAt(0).toUpperCase()}
                      </AvatarFallback>
                    </Avatar>
                  )}
                </div>
                
                <div className="flex-1 space-y-1">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium leading-none">
                      {activity.title}
                    </p>
                    <Badge 
                      variant="secondary" 
                      className={`text-xs ${getActivityColor(activity.type)}`}
                    >
                      {formatDistanceToNow(new Date(activity.timestamp), { 
                        addSuffix: true, 
                        locale: it 
                      })}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {activity.description}
                  </p>
                  {activity.metadata?.account_username && (
                    <p className="text-xs text-muted-foreground">
                      @{activity.metadata.account_username}
                    </p>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}

export default RecentActivity
